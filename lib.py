import json

DATA_FILE = 'data.json'

def load_json():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_json(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4) 