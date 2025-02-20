import paho.mqtt.client as mqtt
import json
from datetime import datetime
from collections import deque

class MQTTClient:
    def __init__(self):
        # MQTT Configuration
        self.config = {
            'BROKER': "192.168.3.59",
            'PORT': 1883,
            'TOPIC': "ehub/data",
            'USERNAME': "pi",
            'PASSWORD': "raspberry",
            'CLIENT_ID': "mqttx_web_client"
        }
        
        # Data storage
        self.latest_data = {
            'ts': None,
            'host': None,
            'data': []
        }
        
        # Keep last 1000 messages in memory
        self.history = deque(maxlen=1000)
        
        # Setup MQTT client
        self.client = mqtt.Client(client_id=self.config['CLIENT_ID'])
        self.client.username_pw_set(self.config['USERNAME'], self.config['PASSWORD'])
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.config['TOPIC'])
        else:
            print(f"Failed to connect, return code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            
            # Store raw data
            self.latest_data = payload
            
            # Add to history
            self.history.append(payload)
            
        except Exception as e:
            print(f"Error processing message: {e}")

    def start(self):
        try:
            self.client.connect(self.config['BROKER'], self.config['PORT'])
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def get_latest_data(self):
        return self.latest_data

    def get_history_data(self, limit=100):
        """Get historical data with limit"""
        return list(self.history)[-limit:]