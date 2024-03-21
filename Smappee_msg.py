import json
import logging

from influxdb import InfluxDBClient

import config #access global variables

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s -  %(levelname)s:  %(message)s')

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def smappee_ProcessMsg(message, client):
    #print("Message Passed! " + message)
    b1 = message
    b2 = b1[2:] #strip of first 2 char
    b3 = b2[:len(b2)-1] #strip off last char
    data = json.loads(b3)
    #print(data)
    #jprint(data)
    config.CT1 = float(data['intervalDatas'][0]['measurements'][0]['value']/1000)
    config.CT2 = float(data['intervalDatas'][1]['measurements'][0]['value']/1000)
    logging.info("CT1:"+str(config.CT1)+" CT2:"+str(config.CT2))    
    #print(client.__dict__)
    client.write_points(
        [{"measurement": "power", "tags": {"source": "smappee"},
          "fields": {"main": config.CT1, "sub": config.CT2}}]
        )
    logging.info("Smappee data has been stored!")

