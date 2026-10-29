"""Bounded, manually invoked public-source probe. No polling or raw-data export."""

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class RelayParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lines = []
        self.parts = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "span" and "spanLiveText" in attrs.get("id", ""):
            self.parts = []
        elif tag == "br" and self.parts is not None:
            self.parts.append(" ")

    def handle_data(self, data):
        if self.parts is not None:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.parts is not None:
            line = " ".join("".join(self.parts).split())
            if line:
                self.lines.append(line)
            self.parts = None


def fetch(base, path, params):
    request = Request(
        base + path,
        data=urlencode(params).encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": base + "/",
            "User-Agent": "BaseballDataFeasibilityProbe/0.1",
        },
    )
    with urlopen(request, timeout=25) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Response exceeds probe size limit")
        return raw.decode("utf-8-sig")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_id")
    parser.add_argument("--series-id", default="0")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{8}[A-Z]{4}\d", args.game_id):
        parser.error("Expected a verified KBO game ID, e.g. YYYYMMDDXXXX0")
    html = fetch(
        "https://www.koreabaseball.com",
        "/Game/LiveTextView2.aspx",
        {
            "leagueId": "1",
            "seriesId": args.series_id,
            "gameId": args.game_id,
            "gyear": args.game_id[:4],
        },
    )
    relay = RelayParser()
    relay.feed(html)
    score = json.loads(
        fetch(
            "https://m.koreabaseball.com",
            "/ws/Kbo.asmx/GetLiveTextScore",
            {
                "le_id": "1",
                "sr_id": args.series_id,
                "g_id": args.game_id,
                "sc_id": "0",
            },
        )
    )
    result = json.loads(score["resultTable"])
    runs = [row["row"][0]["Text"] for row in result["rows"]]
    if not relay.lines or len(runs) != 2:
        raise ValueError("Missing relay lines or score rows; probe did not pass")
    print(
        json.dumps(
            {
                "game_id": args.game_id,
                "relay_lines": len(relay.lines),
                "runs_away_home": runs,
                "relay_sha256": hashlib.sha256(html.encode()).hexdigest(),
                "scope": "historical response only; live completeness and reuse not verified",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
