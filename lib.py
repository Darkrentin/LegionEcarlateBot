import json

DATA_FILE = 'data.json'

def load_json():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_json(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4) 

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"