import requests
import datetime
import json

local = True

url = "http://localhost:5000/coins"

post = {"id" : 0}

response = requests.post(url, json = json.dumps(post)).json()

print(response)