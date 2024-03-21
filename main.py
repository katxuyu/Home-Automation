import paho.mqtt.client as mqtt
import json
import time
import requests
from datetime import datetime, timedelta
import pytz
from influxdb import InfluxDBClient

local = pytz.timezone ("Australia/Sydney")
fmt = '%Y-%m-%dT%H:%M:%SZ'

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
    
def on_connect(client, userdata, flags, rc):
    print("Connected to smappee with result code "+str(rc))
    client.subscribe("servicelocation/17abeaf8-c0c9-4a50-a18a-cb0dd6e0195f/aggregated")

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #import pdb
    #pdb.set_trace()
    b1 = str(msg.payload)
    b2 = b1[2:] #strip of first 2 char
    b3 = b2[:len(b2)-1] #strip off last char
    data = json.loads(b3)
    #print(data)
    #jprint(data)
    CT1 = 0.0
    CT2 = 0.0
    CT1 = float(data['intervalDatas'][0]['measurements'][0]['value']/1000)
    CT2 = float(data['intervalDatas'][1]['measurements'][0]['value']/1000)
    print(datetime.now())
    print("CT1:"+str(CT1)+" CT2:"+str(CT2))
    client = InfluxDBClient('192.168.1.208', 8086, 'root', 'root', 'quirky')
    client.switch_database('quirky')
    #print(client.__dict__)
    client.write_points(
        [{"measurement": "power", "tags": {"source": "smappee", "reading": "aggr5min"},
          "fields": {"main": CT1, "sub": CT2}}]
        )
    
    # Now read GRID wholesale electricity prices
    now = datetime.now()
    if now.minute == 0 or now.minute == 30:
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
            BuyGrid = (Buyfixed + Buylossfactor * variablePriceNow) / 1.1
            SellGrid = (Sellfixed + Selllossfactor * variablePriceNow) / 1.1
            print("Buy_KWh:" +str(BuyGrid) +str(" at ") +str(t))
            half_ago = now + timedelta(minutes=-30)
            half_utc = local.localize(half_ago, is_dst=False)
            half_epoch = half_utc.astimezone(pytz.utc).timestamp()
            client.write_points(
                [{"measurement": "power", 
                  "tags": {"source": "amber", "reading": "past30min"},
                  "time": half_utc,
                  "fields": {"buy": BuyGrid, "sell": SellGrid}}]
            )
        # Now get latest weather data
        url2= 'https://api.climacell.co/v3/weather/realtime'
        datalayers = ['temp', 'cloud_cover', 'humidity', 'precipitation', 'cloud_ceiling',
                      'surface_shortwave_radiation', 'wind_speed', 'baro_pressure']
        querystring = {"lat":"-33.86739", "lon":"151.17475", "unit_system":"si",
                       "apikey":"9U22L870pxb6ilqSuN6RQOUQJaSIxg8Y", "fields": datalayers}
        r2 = requests.get(url2, params= querystring ) 
        if r2.status_code != 200:
            print("We have problem accessing Climacell API "+str(r2.status_code))
        else:
            #print("Climacell API is sweet "+str(r.status_code))
            data2 = r2.json()
            temperature = float(data2['temp']['value'])
            print('ClimaCell temp now is '+str(temperature))    
            humidity = float(data2['humidity']['value'])
            precipitation = float(data2['precipitation']['value'])
            cloud_cover = float(data2['cloud_cover']['value'])
            radiation = float(data2['surface_shortwave_radiation']['value'])
            wind_speed = float(data2['wind_speed']['value'])
            baro_pressure = float(data2['baro_pressure']['value'])
            client.write_points([{"measurement": "weather", "tags": {"source": "climacell", "type": "realtime"},
                                  "fields": {"Temperature": temperature, "Humidity": humidity,
                                             "Cloud cover": cloud_cover, 
                                             "Radiation": radiation, "Precipitation": precipitation,
                                             "Wind speed": wind_speed, "Baro pressure": baro_pressure }}]
            )
    
        
smappee1 = mqtt.Client()
smappee1.on_connect = on_connect
smappee1.on_message = on_message
smappee1.connect("192.168.1.204", 1883)
smappee1.loop_forever()