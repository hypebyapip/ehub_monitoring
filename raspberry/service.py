import time
from data_generator import DataGenerator
from mqtt_handler import MQTTHandler
from database_handler import DatabaseHandler
from config import MQTT_CONFIG, DB_CONFIG

# Create database URL
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def main():
    # Initialize components
    generator = DataGenerator(DB_URL)
    mqtt_handler = MQTTHandler(MQTT_CONFIG)
    db_handler = DatabaseHandler(DB_URL)
    
    print("Starting data generation and transmission...")
    print(f"MQTT Broker: {MQTT_CONFIG['BROKER']}:{MQTT_CONFIG['PORT']}")
    print(f"MQTT Topic: {MQTT_CONFIG['TOPIC']}")
    
    try:
        while True:
            # Generate data
            data, timestamp = generator.generate_data()
            
            if data and timestamp:
                # Save to database
                try:
                    db_handler.save_all_data(data)
                    print("Data saved to database")
                except Exception as e:
                    print(f"Error saving to database: {e}")
                
                # Publish to MQTT
                try:
                    mqtt_handler.publish_data(data)
                except Exception as e:
                    print(f"Error publishing to MQTT: {e}")
            
            # Wait before next iteration
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping application...")
        mqtt_handler.disconnect()
        generator.cleanup()
        print("Application stopped")

if __name__ == "__main__":
    main()