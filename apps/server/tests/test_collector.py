import json

import pytest

from workers.collect import collect_snapshot

HTML = '<span id="x_spanLiveText" class="play">타자 &amp; 결과<br/>안내</span>'


def score_response(runs):
    return json.dumps(
        {"resultTable": json.dumps({"rows": [{"row": [{"Text": str(run)}]} for run in runs]})}
    )


def test_semantic_hash_ignores_markup_but_tracks_score_changes(monkeypatch):
    html, runs = HTML, [3, 1]

    def fetch(base, path, params):
        return html if "aspx" in path else score_response(runs)

    monkeypatch.setattr("workers.collect.fetch", fetch)
    first = collect_snapshot("20260901LGOB0", "0")
    html = "<!-- volatile page markup -->" + HTML
    assert collect_snapshot("20260901LGOB0", "0").content_hash == first.content_hash
    runs = [4, 1]
    assert collect_snapshot("20260901LGOB0", "0").content_hash != first.content_hash
    assert first.away_team_id == "LG"
    assert first.home_team_id == "OB"
    assert first.relay_line_count == 1


def test_error_html_does_not_become_a_successful_empty_game(monkeypatch):
    monkeypatch.setattr("workers.collect.fetch", lambda *args: "<html>Error</html>")
    with pytest.raises(ValueError):
        collect_snapshot("20260901LGOB0", "0")
