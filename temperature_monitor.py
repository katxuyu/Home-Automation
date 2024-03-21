from mqtt_publisher import connect_to_broker, publish_command
import random
import time

def get_temperature():
    # Simulate temperature reading
    return random.randint(18, 30)

def main():
    connect_to_broker()
    while True:
        temp = get_temperature()
        print(f"Current temperature: {temp}°C")
        if temp > 25:
            publish_command("TURN_ON")
        else:
            publish_command("TURN_OFF")
        time.sleep(5)  # Wait for 5 seconds before reading the temperature again

if __name__ == "__main__":
    main()
