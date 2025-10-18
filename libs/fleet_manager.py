from . import lib
import unicodedata
import re

async def generate_ship_name_list():
    ship_name_list = []

    data = await lib.load_json(lib.SHIP_LIST)
    if data:
        for ship in data:
            ship_name_list.append(ship)
    
    return ship_name_list

def format_name(name: str):
    nfkd_form = unicodedata.normalize('NFD', name)
    ascii_name = nfkd_form.encode('ascii', 'ignore').decode('utf-8')
    lower_name = ascii_name.lower()
    spaced_name = re.sub(r'[^a-z0-9]+', ' ', lower_name)
    formatted_name = spaced_name.strip().replace(' ', '-')
    if not ("super-hornet" in formatted_name):
        formatted_name=formatted_name.replace("mk-ii","mkii")

    if formatted_name=="mercury":
        formatted_name="mercury-star-runner"
    return formatted_name

def create_ship_save(name,id):
    ship={}
    ship["id"]=str(id)
    ship["itemType"]="SHIP"
    ship["x"]="0.0"
    ship["y"]="0.0"
    ship["topRotation"]="0.0"
    ship["zoom"]="1.0"
    ship["viewAngle"]="iso"
    ship["imageRes"]="l"
    ship["imageScale"]="1"
    ship["dropShadow"]="true"
    ship["shipSlug"]=format_name(name)
    ship["variantSlug"]=""
    ship["width"]="0"
    ship["height"]="0"
    ship["autoPositionDistance"]="0"
    ship["autoPositionAlignment"]="Alignment.bottomCenter"
    ship["defaultText"]="TEST"
    ship["parentOfGroup"]="42"

    return ship 

def create_fleet_save(data):
    save = {}
    save["type"]="starjumpFleetviewer"
    save["version"]=1
    save["backgroundColor"]="0c000000"
    save["canvasZoom"]="0.1"
    save["canvasPanX"]="0"
    save["canvasPanY"]="0"
    save["shipScaleFactor"]="4.0"
    save["minZoom"]="0.0010000000"
    save["maxZoom"]="1.0000000000"
    save["canvasItems"] = []

    i = 1
    for player in data:
        for s in data[player]["InGame"]:
            save["canvasItems"].append(create_ship_save(s,i))
            i+=1
    for player in data:
        for s in data[player]["OnRSI"]:
            save["canvasItems"].append(create_ship_save(s,i))
            i+=1
    return save

def create_fleet_on_rsi_save(data):
    save = {}
    save["type"]="starjumpFleetviewer"
    save["version"]=1
    save["backgroundColor"]="0c000000"
    save["canvasZoom"]="0.1"
    save["canvasPanX"]="0"
    save["canvasPanY"]="0"
    save["shipScaleFactor"]="4.0"
    save["minZoom"]="0.0010000000"
    save["maxZoom"]="1.0000000000"
    save["canvasItems"] = []

    i = 1
    for player in data:
        for s in data[player]["OnRSI"]:
            save["canvasItems"].append(create_ship_save(s,i))
            i+=1
    return save

