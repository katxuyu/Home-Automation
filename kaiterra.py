import requests
import json
from datetime import datetime
from influxdb import InfluxDBClient

url = "https://api.kaiterra.cn/v1/lasereggs/00000000-0001-0001-0000-00007e57c0de"
key = {"key": "MzVlYTE3M2ExYTQ3NDYyYmE0MTk0MDJkN2JhMTY2NWIxZWNk"}

r = requests.get(url, params=key )
if r.status_code != 200:
    print("We have problem accessing Kaiterra API "+str(r.status_code))
else:
    print("Kaiterra API is sweet "+str(r.status_code))
    data2 = r.json()
    humidity = int(data2['info.aqi']['data']['humidity'])
    pm10 = int(data2['info.aqi']['data']['pm10'])
    pm25 = int(data2['info.aqi']['data']['pm25'])
    rtvoc = int(data2['info.aqi']['data']['rtvoc'])
    temp = int(data2['info.aqi']['data']['temp'])
    print("Kaiterra Temp is "+str(temp))
    client = InfluxDBClient('192.168.1.205', 8086, 'root', 'root', 'power')
    client.write_points(
            [{"measurement": "kaiterra", "tags": {"Poll": "5min"},
              "fields": {"Humidity": humidity, "PM10": pm10, "PM2.5": pm25, "RTVOC": rtvoc, "Temp": temp}}],
        )
        