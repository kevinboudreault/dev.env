import os
from dotenv import load_dotenv

import datetime
import json
import requests

load_dotenv()


# Vars
now = datetime.datetime.now()
fnow = now.strftime("%Y%m%d_%H")

lat = os.environ.get('lat')
lon = os.environ.get('lon')
api_key = os.environ.get('weather_api_key')
fs_path = os.environ.get('weather_save_path')

print(f"Getting weather for {lat},{lon}")

url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"


# Check if dir path doesn't exist >  create dir first

isDirExist = os.path.exists(fs_path)
if not isDirExist:
    os.makedirs(fs_path)



filePath = fs_path + fnow + ".json"

# if file doesn't exist or is empty > pull data to save to it
if (not os.path.exists(filePath)) or (os.stat(filePath).st_size == 0) :
    
    # Requests data
    responseData = requests.get(url)
    jsonData = responseData.text
    
    # Save json to file path
    with open(filePath, 'w') as jsonFile:
        jsonFile.write(json.dumps(jsonData))
