import json
from pathlib import Path
import shutil
from datetime import datetime

DATA="data/data.json"
SHIP_LIST="data/shipList.json"
SHIP_DB="data/shipDB.json"
FLEET="data/fleet.json"
SAVE="data/save.json"

BASE_PATH = Path(__file__).parent.parent

# Fichiers à sauvegarder automatiquement
BACKUP_FILES = [DATA, FLEET]

def load_json(filename: str):
    filepath = BASE_PATH / filename
    if not filepath.exists():
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def create_backup(filename: str):
    """Crée une copie de backup d'un fichier JSON."""
    filepath = BASE_PATH / filename
    if not filepath.exists():
        return
    
    backup_path = BASE_PATH / f"{filename}.backup"
    try:
        shutil.copy2(filepath, backup_path)
    except Exception as e:
        print(f"Erreur lors de la création du backup de {filename}: {e}")

def save_json(data: dict, filename: str):
    """Sauvegarde un fichier JSON avec backup automatique."""
    filepath = BASE_PATH / filename
    
    # Créer un backup avant de sauvegarder (si c'est un fichier à backup)
    if filename in BACKUP_FILES and filepath.exists():
        create_backup(filename)
    
    # Sauvegarder le fichier
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def format_time(seconds: int) -> str:
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"

def restore_from_backup(filename: str):
    """Restaure un fichier depuis son backup."""
    filepath = BASE_PATH / filename
    backup_path = BASE_PATH / f"{filename}.backup"
    
    if not backup_path.exists():
        raise FileNotFoundError(f"Aucun backup trouvé pour {filename}")
    
    try:
        shutil.copy2(backup_path, filepath)
        print(f"Fichier {filename} restauré depuis le backup")
        return True
    except Exception as e:
        print(f"Erreur lors de la restauration de {filename}: {e}")
        return False

def init_data():
    data={}
    data["time_seed"]=0
    data["timer_msg_id"]=0
    data["timer_channel_id"]=0
    data["players"]=[]

    return data