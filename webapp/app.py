from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from mqtt_client import MQTTClient
from routes.monitoring import monitoring_bp
# from routes.api import api_bp
from routes.settings import settings_bp  # Import the new settings blueprint

# Database setup
Base = declarative_base()
engine = create_engine('postgresql://postgres:1234@localhost/db_ehub')
Session = sessionmaker(bind=engine)
db_session = Session()

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/db_ehub'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize MQTT Client
    mqtt_client = MQTTClient()
    mqtt_client.start()
    
    # Register blueprints
    app.register_blueprint(monitoring_bp)
    # app.register_blueprint(api_bp)
    app.register_blueprint(settings_bp)  # Register the settings blueprint
    
    # Add url_for to be used in templates
    @app.context_processor
    def utility_processor():
        return dict(
            monitoring=monitoring_bp,
            history=None,  # Add these when implemented
            scc=settings_bp,     # Add settings blueprint references
            bms=settings_bp,
            site_tenant=settings_bp,
            user=settings_bp
        )
    
    # Add mqtt_client to app context
    app.mqtt_client = mqtt_client
    
    # Add database session to app context
    app.db_session = db_session
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)