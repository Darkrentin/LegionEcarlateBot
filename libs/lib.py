import json
from pathlib import Path
import aiofiles

DATA="data/data.json"
SHIP_LIST="data/shipList.json"
SHIP_DB="data/shipDB.json"
FLEET="data/fleet.json"

BASE_PATH = Path(__file__).parent.parent

async def load_json(filename: str):
    filepath = BASE_PATH / filename
    if not filepath.exists():
        return None
    try:
        async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return None

async def save_json(data: dict, filename: str):
    filepath = BASE_PATH / filename
    # S'assurer que le dossier parent existe
    filepath.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))

def format_time(seconds: int) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"