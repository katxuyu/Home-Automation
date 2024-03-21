"""
This process checks clock and at certian
times will trigger events such as API calls
"""

import requests
from datetime import datetime, timedelta
import pytz
from influxdb import InfluxDBClient
import logging

import config #access global variables
local = pytz.timezone(config.timezone_name)
fmt = '%Y-%m-%dT%H:%M:%SZ'


logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s -  %(levelname)s:  %(message)s')


def check_clock(client):
    #print("First")
    now = datetime.now()
    #print("Second")
    if now.minute == 0 or now.minute == 30: # every 1/2 hour
        #print("Third")
        # Read wholesale electricity prices using amber API
        url = config.amber_url
        postcode = {"postcode": config.amber_postcode}
        r = requests.post(url, json = postcode)
        data = r.json()
        if (r.status_code) != 200:
            logging.info("There is API error with Amber Electric "+ str(r.status_code))
        else:
            #print("This is else")
            Buyfixed = float(data['data']['staticPrices']['E1']['totalfixedKWHPrice'])
            Buylossfactor = float(data['data']['staticPrices']['E1']['lossFactor'])
            Sellfixed = float(data['data']['staticPrices']['B1']['totalfixedKWHPrice'])
            Selllossfactor = float(data['data']['staticPrices']['B1']['lossFactor'])
            variablePrices = data['data']['variablePricesAndRenewables']   
            variablePriceNow = float(variablePrices[0]['wholesaleKWHPrice'])
            #jprint(variablePrice)
            #jprint(variablePrices[0])
            config.BuyGrid = (Buyfixed + Buylossfactor * variablePriceNow) / 1.1
            config.SellGrid = (Sellfixed + Selllossfactor * variablePriceNow) / 1.1
            logging.info("Buy_KWh:" +str(config.BuyGrid) +str(" at ") +str(now))
            half_ago = now + timedelta(minutes=-30)
            half_utc = local.localize(half_ago, is_dst=False)
            #half_epoch = half_utc.astimezone(pytz.utc).timestamp()
            client.write_points(
                [{"measurement": "power", 
                  "tags": {"source": "amber", "reading": "past30min"},
                  "time": half_utc,
                  "fields": {"buy": config.BuyGrid, "sell": config.SellGrid}}]
            )
        # Now get latest weather data
        datalayers = ['temp', 'cloud_cover', 'humidity', 'precipitation', 'cloud_ceiling',
                      'surface_shortwave_radiation', 'wind_speed', 'baro_pressure']
        querystring = {"lat":config.home_lat, "lon":config.home_long, "unit_system":"si",
                       "apikey":config.climacell_api, "fields": datalayers}
        r2 = requests.get(config.climacell_realtime_url, params= querystring ) 
        if r2.status_code != 200:
            logging.error("We have problem accessing Climacell API "+str(r2.status_code))
        else:
            #print("Climacell API is sweet "+str(r.status_code))
            data2 = r2.json()
            temperature = float(data2['temp']['value'])
            logging.error('ClimaCell temp now is '+str(temperature))    
            humidity = float(data2['humidity']['value'])
            precipitation = float(data2['precipitation']['value'])
            cloud_cover = float(data2['cloud_cover']['value'])
            config.radiation = float(data2['surface_shortwave_radiation']['value'])
            wind_speed = float(data2['wind_speed']['value'])
            baro_pressure = float(data2['baro_pressure']['value'])
            client.write_points([{"measurement": "weather", "tags": {"source": "climacell", "type": "realtime"},
                                  "fields": {"Temperature": temperature, "Humidity": humidity, "Cloud cover": cloud_cover, 
                                             "Radiation": config.radiation, "Precipitation": precipitation,
                                             "Wind speed": wind_speed, "Baro pressure": baro_pressure }}]
            )
        logging.info("The data have been stored!")
    
            
    if now.hour == 0 and now.minute == 0: # the below code will only need to execute once per day
        #print("Fourth")
        t2 = now + timedelta(days=1)
        fmt = '%Y-%m-%dT%H:%M:%SZ'
        t1 = now.strftime(fmt)
        tomor = t2.strftime(fmt)
        datalayers = ['temp', 'feels_like', 'cloud_cover', 'humidity', 'precipitation', 'precipitation_probability', 'cloud_ceiling', 
                      'surface_shortwave_radiation', 'wind_speed', 'wind_direction', 'baro_pressure']
        querystring = {"lat": config.home_lat, "lon":config.home_long, "unit_system":"si", "start_time": now, "end_time": tomor, 
                       "apikey":config.climacell_api, "fields": datalayers}
        r = requests.get(config.climacell_forecast_url, params= querystring ) 
        if r.status_code != 200:
            logging.error("We have problem accessing Climacell API "+str(r.text))
        else:
            logging.info("Climacell API is sweet "+str(r.status_code))
            records = normalize_json_data(r.json())
            client.write_points(records, time_precision='s')
        logging.info("The data have been stored!")
            
def time_to_epoch(ob_time):
    dt =  date_parse(ob_time)
    epoch = calendar.timegm(dt.timetuple())
    return epoch
    
def normalize_json_data(json_data):
    records = []
    for i in json_data:
        points = {}
        fields = {}
        fields = {'temp': i.get('temp').get('value'),
                  'precipitation': i.get('precipitation').get('value'),
                  'precipitation_probability': i.get('precipitation_probability').get('value'),
                  'feels_like': i.get('feels_like').get('value'),
                  'humidity': i.get('humidity').get('value'),
                  'baro_pressure': i.get('baro_pressure').get('value'),
                  'wind_speed': i.get('wind_speed').get('value'),
                  'wind_direction': i.get('wind_direction').get('value'),
                  'cloud_cover': i.get('cloud_cover').get('value'),
                  'cloud_ceiling': i.get('cloud_ceiling').get('value'),
                  'surface_shortwave_radiation': i.get('surface_shortwave_radiation').get('value'),
                  }
        observation_time = time_to_epoch(i.get('observation_time').get('value'))
        points = {"measurement": "forecast", 
                  "tags": {"source": "climacell"},
                  'time': observation_time,
                  "fields": fields}
        records.append(points)
    return records


