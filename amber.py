import requests
import json
from datetime import datetime

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
url = "https://api.amberelectric.com.au/prices/listprices"
postcode = {"postcode": "2039"}

r = requests.post(url, json = postcode)
data = r.json()

if (r.status_code) != 200:
    print("shit, we have API error "+ str(r.status_code))
else:
    Buyfixed = float(data['data']['staticPrices']['E1']['totalfixedKWHPrice'])
    Buylossfactor = float(data['data']['staticPrices']['E1']['lossFactor'])
    Sellfixed = float(data['data']['staticPrices']['B1']['totalfixedKWHPrice'])
    Selllossfactor = float(data['data']['staticPrices']['B1']['lossFactor'])
    variablePrices = data['data']['variablePricesAndRenewables']   
    variablePriceNow = float(variablePrices[0]['wholesaleKWHPrice'])
    #jprint(variablePrice)
    #jprint(variablePrices[0])
    BuyGrid = Buyfixed + Buylossfactor * variablePriceNow / 1.1
    SellGrid = Sellfixed + Selllossfactor * variablePriceNow / 1.1    
    