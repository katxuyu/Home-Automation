import paho.mqtt.client as mqtt
import json
import logging

#import config #access globla variables

#Connections Corner
#from MainProcess import *

#Messages Corner
from Smappee_msg import *

logging.basicConfig(filename='app.log',level=logging.INFO, format='%(asctime)s -  %(levelname)s:  %(message)s')

   
def processMessages(client, userdata, msg, influx_client):
    #print("Message Received!")
    m_topic =  msg.topic #Topic that the message is subscribing
    m_decode = str(msg.payload.decode("utf-8")) #Converting the message to string format
    #m_json = json.loads(m_decode) #Coverting the message to json format
    #print("Power: " + str(m_json["ENERGY"]["Power"]))
    logging.info("Topic: "+ m_topic)

    if m_topic == "tele/tasmota_683910/SENSOR": #IF the connection is from Sonoff
        logging.info("Message Received from SonoffPOW SENSOR")

    elif m_topic == "servicelocation/17abeaf8-c0c9-4a50-a18a-cb0dd6e0195f/aggregated": #IF the message is from Smappee
        logging.info("Message Received from Smappee")
        smappee_ProcessMsg(m_decode, influx_client)
   
    elif m_topic == "tele/tasmota_683910/LWT":
        logging.info("Message Received from SonoffPOW LWT: " + m_decode)

    elif m_topic == "mini1/PB":
        logging.info("Message Recieved from Mini1: " + m_decode)

    elif m_topic == "mini2/PB":
        logging.info("Message Received from Mini2: " + m_decode)
