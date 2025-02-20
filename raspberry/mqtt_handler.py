import paho.mqtt.client as mqtt
import json

class MQTTHandler:
    def __init__(self, config):
        self.client = mqtt.Client(client_id=config['CLIENT_ID'])
        self.client.username_pw_set(config['USERNAME'], config['PASSWORD'])
        self.topic = config['TOPIC']
        
        try:
            self.client.connect(config['BROKER'], config['PORT'])
            self.client.loop_start()
            print(f"Connected to MQTT Broker at {config['BROKER']}:{config['PORT']}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")

    def publish_data(self, data):
        try:
            message = json.dumps(data)
            result = self.client.publish(self.topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published message to {self.topic}")
            else:
                print(f"Failed to publish message, error code: {result.rc}")
        except Exception as e:
            print(f"Error publishing message: {e}")

    def disconnect(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
            print("Disconnected from MQTT broker")
        except Exception as e:
            print(f"Error disconnecting from MQTT broker: {e}")