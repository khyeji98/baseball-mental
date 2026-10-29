import json
from pathlib import Path

from app.config import Settings
from app.main import create_app

# Schema generation never connects to a database or reads deployment credentials.
app = create_app(Settings(_env_file=None, mongodb_uri=None))
target = Path(__file__).resolve().parents[2] / "contracts" / "openapi.json"
target.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n")
