from pathlib import Path
import requests
import json
import lib

from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Url = "https://api.star-citizen.wiki/api/v3/vehicles?page=1&limit=1000&locale=en_EN"
script_dir = Path(__file__).parent

DataBaseType = "Stardle" # All / Stardle / Simple

def generate_ship_data_base():
    data = requests.get(Url, verify=False)
    if data.status_code != 200:
        raise Exception("Error with reception of data")

    try:
        data = data.json()
    except:
        print("Error in generate data base")

    ShipName = {}
    ShipDB = {}

    for ship in data["data"]:
        ShipName[ship["name"]] = ship["link"]
        
        ShipUrl = f"https://api.star-citizen.wiki/api/v3/vehicles/{ship["name"]}?locale=en_EN"
        ShipData = requests.get(ShipUrl, verify=False)
        if(ShipData.status_code != 200 or "data" not in ShipData.json()):
            print(f"Error with reception of data for {ship['name']}")
            continue
        
        print("Data received for", ship["name"])
        ShipData = ShipData.json()["data"]
        Ship = {}

        #get only the parameters we need
        if DataBaseType == "Stardle":
            Ship["name"] = ShipData["name"]
            Ship["manufacturer"] = ShipData["manufacturer"]["name"]
            Ship["role"] = ShipData["foci"]
            Ship["length"] = ShipData["sizes"]["length"]
            
            Ship["value"] = ShipData["skus"]
            if(len(Ship["value"]) > 0):
                Ship["value"] = Ship["value"][0]["price"]
            else:
                Ship["value"] = "N/A"
            
            Ship["cargo"] = ShipData["cargo_capacity"]
            if(ShipData["crew"]["max"] == None):
                Ship["crew"] = ShipData["crew"]["min"]
            else:
                Ship["crew"] = ShipData["crew"]["max"]
            Ship["release_year"] = "" #Not Implemented

            ShipDB[ship["name"]] = Ship

        #or get all the parameters
        elif DataBaseType == "All":
            ShipDB[ship["name"]] = ShipData
        
        ShipName[ship["name"]] = ShipUrl

    lib.save_json(ShipName, lib.SHIP_LIST)
    lib.save_json(ShipDB,lib.SHIP_DB)

if __name__ == "__main__":

    generate_ship_data_base()
