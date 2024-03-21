import json
import requests
import calendar
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
from dateutil.parser import parse as date_parse

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
        

t1 = datetime.now()
#if t1.hour == 0 and t1.minute == 0: # the below code will only need to execute once per day
if True:
    t2 = t1 + timedelta(days=1)
    fmt = '%Y-%m-%dT%H:%M:%SZ'
    now = t1.strftime(fmt)
    tomor = t2.strftime(fmt)
    url= 'https://api.climacell.co/v3/weather/forecast/hourly'
    datalayers = ['temp', 'feels_like', 'cloud_cover', 'humidity', 'precipitation', 'precipitation_probability', 'cloud_ceiling', 
                  'surface_shortwave_radiation', 'wind_speed', 'wind_direction', 'baro_pressure']
    querystring = {"lat":"-33.86739", "lon":"151.17475", "unit_system":"si", "start_time": now, "end_time": tomor, 
                   "apikey":"9U22L870pxb6ilqSuN6RQOUQJaSIxg8Y", "fields": datalayers}
    r = requests.get(url, params= querystring ) 
    if r.status_code != 200:
        print("We have problem accessing Climacell API "+str(r.text))
    else:
        print("Climacell API is sweet "+str(r.status_code))
        records = normalize_json_data(r.json())
        client = InfluxDBClient('192.168.1.210', 8086, 'root', 'root', 'quirky')
        client.switch_database('quirky')
        client.write_points(records, time_precision='s')
        
        
        
        
        