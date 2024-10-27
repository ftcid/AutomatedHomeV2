import paho.mqtt.client as mqtt
import datetime
import time
import sys

topic_time = '/global/datetime/time'
topic_date = '/global/datetime/date'

# Function to publish the current date and time to separate topics
def publish_date_and_time(client):
    # Get current date and time
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    # Publish the date
    client.publish(topic_date, current_date)
    print(f"Published date: {current_date} to topic {topic_date}")

    # Publish the time
    client.publish(topic_time, current_time)
    print(f"Published time: {current_time} to topic {topic_time}")

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to the MQTT broker")
    else:
        print(f"Failed to connect with result code {rc}")

# Function to wait until the beginning of the next minute
def wait_for_next_minute():
    now = datetime.datetime.now()
    # Calculate how many seconds remain until the next minute
    seconds_until_next_minute = 60 - now.second
    print(f"Waiting {seconds_until_next_minute} seconds for the next minute to start...")
    time.sleep(seconds_until_next_minute)

# Main function
def main():
    # Check if broker and port arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python3 datetime_publisher.py <broker_address> <port>")
        print("Example: python3 datetime_publisher.py test.mosquitto.org 1883")
        sys.exit(1)

    # Get the broker and port from command-line arguments
    broker = sys.argv[1]
    port = int(sys.argv[2])

    # Create an MQTT client instance
    client = mqtt.Client()

    # Assign the on_connect callback
    client.on_connect = on_connect

    # Connect to the broker
    try:
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker {broker} on port {port}: {e}")
        sys.exit(1)

    # Start the MQTT client
    client.loop_start()

    try:
        while True:
            # Wait until the start of the next minute
            wait_for_next_minute()

            # Publish the date and time
            publish_date_and_time(client)
    except KeyboardInterrupt:
        print("Disconnecting from broker")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

