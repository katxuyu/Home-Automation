import paho.mqtt.client as mqtt

# MQTT settings
broker_address = "your_mqtt_broker_address"
port = 1883  # Default MQTT port
topic = "home/commands"

# Create a new MQTT client instance
client = mqtt.Client("PiPublisher")

def connect_to_broker():
    client.connect(broker_address, port=port)
    print("Connected to MQTT Broker")

def publish_command(command):
    client.publish(topic, command)
    print(f"Published command {command} to topic {topic}")
