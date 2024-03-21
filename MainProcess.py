"""
Creates multiple Connections to a broker 
and sends and receives messages.
Uses one thread per client
"""
import paho.mqtt.client as mqtt
import time
import json
import threading
import logging
from influxdb import InfluxDBClient
from ProcessMessage import *
from CheckClock import *
#from Control import *

import config # access global variables

logging.basicConfig(filename='app.log',level=logging.INFO, format='%(asctime)s -  %(levelname)s:  %(message)s')
logging.info("Logging is open")

influx_client = InfluxDBClient('192.168.1.208', 8086, 'root', 'root', 'quirky')
influx_client.switch_database('quirky')

clients=[
        {"broker":"192.168.1.204","port":1883,"name":"Smappee","sub_topic":"servicelocation/17abeaf8-c0c9-4a50-a18a-cb0dd6e0195f/aggregated"},
        {"broker":"192.168.1.208","port":1883,"name":"Pre-prod","sub_topic":"tele/tasmota_683910/SENSOR;tele/tasmota_683910/LWT;mini1/PB;mini2/PB","pub_topic":"test1"},
        
        ]


nclients=len(clients)
message="test message"

def Connect(client,broker,port,keepalive,run_forever=False):
    """Attempts connection set delay to >1 to keep trying
    but at longer intervals. If runforever flag is true then
    it will keep trying to connect or reconnect indefinetly otherwise
    gives up after 3 failed attempts"""
    connflag=False
    delay=5
    #print("connecting ",client)
    badcount=0 # counter for bad connection attempts
    while not connflag:
        logging.info("connecting to broker "+str(broker))
        #print("connecting to broker "+str(broker)+":"+str(port))
        logging.info("Attempts", str(badcount))
        time.sleep(delay)
        try:
            client.connect(broker,port,keepalive)
            connflag=True

        except:
            client.badconnection_flag=True
            logging.warning("connection failed "+str(badcount))
            badcount +=1
            if badcount>=3 and not run_forever: 
                return -1
                raise SystemExit #give up       
    return 0
    #####end connecting
 
def wait_for(client,msgType,period=1,wait_time=10,running_loop=False):
    """Will wait for a particular event gives up after period*wait_time, Default=10
seconds.Returns True if succesful False if fails"""
    #running loop is true when using loop_start or loop_forever
    client.running_loop=running_loop #
    wcount=0  
    while True:
        logging.info("waiting"+ msgType)
        if msgType=="CONNACK":
            if client.on_connect:
                if client.connected_flag:
                    return True
                if client.bad_connection_flag: #
                    return False
                
        if msgType=="SUBACK":
            if client.on_subscribe:
                if client.suback_flag:
                    return True
        if msgType=="MESSAGE":
            if client.on_message:
                if client.message_received_flag:
                    return True
        if msgType=="PUBACK":
            if client.on_publish:        
                if client.puback_flag:
                    return True
     
        if not client.running_loop:
            client.loop(.01)  #check for messages manually
        time.sleep(period)
        wcount+=1
        if wcount>wait_time:
            print("return from wait loop taken too long")
            return False
    return True

def client_loop(client,broker,port,keepalive=60,loop_function=None,\
             loop_delay=1,run_forever=False):
    """runs a loop that will auto reconnect and subscribe to topics
    pass topics as a list of tuples. You can pass a function to be
    called at set intervals determined by the loop_delay
    """
    client.run_flag=True
    client.broker=broker
    logging.info("running loop ")
    client.reconnect_delay_set(min_delay=1, max_delay=12)
      
    while client.run_flag: #loop forever

        if client.bad_connection_flag:
            break         
        if not client.connected_flag:
            logging.info("Connecting to ",broker)
            if Connect(client,broker,port,keepalive,run_forever) !=-1:
                if not wait_for(client,"CONNACK"):
                   client.run_flag=False #break no connack
            else:#connect fails
                client.run_flag=False #break
                logging.warning("quitting loop for  broker ",broker)

        client.loop(0.01)

        if client.connected_flag and loop_function: #function to call
                loop_function(client,loop_delay) #call function
    time.sleep(1)
    logging.info("disconnecting from",broker)
    if client.connected_flag:
        client.disconnect()
        client.connected_flag=False
    
def on_log(client, userdata, level, buf):
   print(buf)

def on_message(client, userdata, message):
   time.sleep(1)
   #print("message received",str(message.payload.decode("utf-8")))
   processMessages(client, userdata, message, influx_client)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        for c in clients:
          if client==c["client"]:
              if c["sub_topic"]!="":
                  sub_topics = c["sub_topic"].split(";")
                  for topic in sub_topics:
                      print(topic)
                      client.subscribe(topic)
          
        logging.info("Connected OK")
    else:
        logging.error("Bad connection Returned code=",rc)
        client.loop_stop()  

def on_disconnect(client, userdata, rc):
   client.connected_flag=False #set flag
   #print("client disconnected ok")

def on_publish(client, userdata, mid):
   time.sleep(1)
   logging.info("In on_pub callback mid= "  ,mid)

def pub(client,loop_delay):
    #print("in publish")
    pass

def Create_connections():
   for i in range(nclients):
      cname="client"+str(i)
      t=int(time.time())
      client_id =cname+str(t) #create unique client_id
      client = mqtt.Client(client_id)             #create new instance
      clients[i]["client"]=client 
      clients[i]["client_id"]=client_id
      clients[i]["cname"]=cname
      broker=clients[i]["broker"]
      port=clients[i]["port"]
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      #client.on_publish = on_publish
      client.on_message = on_message
      t = threading.Thread(target\
            =client_loop,args=(client,broker,port,60,pub))
      threads.append(t)
      t.start()


mqtt.Client.connected_flag=False #create flag in class
mqtt.Client.bad_connection_flag=False #create flag in class

threads=[]
logging.info("Creating Connections ")
no_threads=threading.active_count()
#print("current threads =",no_threads)
logging.info("Publishing ")
Create_connections()

logging.info("All clients connected ")
no_threads=threading.active_count()
#print("current threads =",no_threads)
logging.info("starting main loop")
try:
    while True:
        time.sleep(10)
        no_threads=threading.active_count()
        #print("current threads =",no_threads)
        for c in clients:
            if not c["client"].connected_flag:
                logging.info("broker ",c["broker"]," is disconnected")
        check_clock(influx_client)
        #do_control()

except KeyboardInterrupt:
    print("ending")
    for c in clients:
        c["client"].run_flag=False
time.sleep(10)
