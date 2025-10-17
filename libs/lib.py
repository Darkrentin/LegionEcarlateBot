import json
from pathlib import Path

DATA="data/data.json"
SHIP_LIST="data/shipList.json"
SHIP_DB="data/shipDB.json"
FLEET="data/fleet.json"

BASE_PATH = Path(__file__).parent.parent

def load_json(filename: str):
    filepath = BASE_PATH / filename
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def save_json(data: dict, filename: str):
    filepath = BASE_PATH / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def format_time(seconds: int) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"