MQTT_CONFIG = {
    'BROKER': "192.168.3.59",
    'PORT': 1883,
    'TOPIC': "ehub/data",
    'USERNAME': "pi",
    'PASSWORD': "raspberry",
    'CLIENT_ID': "ehub"
}

DB_CONFIG = {
    'host': 'localhost',
    'database': 'db_ehub',
    'user': 'postgres',
    'password': '1234',
    'port': '5432'
}

# Create database URL for SQLAlchemy
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"