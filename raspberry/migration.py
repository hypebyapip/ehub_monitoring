from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import (
    Base, SiteData, DeviceInfo, User, SCCConfig, 
    BMSConfig, Tenant, AlarmThreshold, LVDSettings
)
import bcrypt
import json
from config import DB_CONFIG

def init_db():
    """Initialize database and create all tables"""
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(db_url)
    Base.metadata.drop_all(engine)  # Drop existing tables
    Base.metadata.create_all(engine)  # Create new tables
    return engine

def create_initial_data(engine):
    """Create initial static data for database"""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create admin user
        password = '1234'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin = User(
            username='admin',
            password=hashed.decode('utf-8'),
            level='admin'
        )
        session.add(admin)
        print("Admin user created successfully")

        # Create site data
        site = SiteData(
            site_id='SITE001',
            site_name='Pusat Energi Terbarukan',
            address='Jl. Teknologi No. 42, Kota Maju',
            ip_address='192.168.3.59',
            net_mask='255.255.255.0',
            gateway='192.168.3.1'
        )
        session.add(site)
        print("Site data created successfully")

        # Create device info
        device = DeviceInfo(
            serial_number='EH-001-2024',
            device_model='EHUB-X1',
            part_number='EHUB-PN-001',
            software_ver='1.0.0',
            hardware_ver='1.1'
        )
        session.add(device)
        print("Device info created successfully")

        # Create BMS Configuration
        bms_config = BMSConfig(
            vendor_name='PT. Sundaya Indonesia',
            battery_type='Talis 30',
            num_of_pack=2
        )
        session.add(bms_config)
        print("BMS configuration created successfully")

        # Create SCC Configurations
        scc_configs = [
            SCCConfig(
                scc_number=1,
                is_active=True,
                ip_address='192.168.3.61',
                modbus_address='1'
            ),
            SCCConfig(
                scc_number=2,
                is_active=True,
                ip_address='192.168.3.62',
                modbus_address='2'
            )
        ]
        # Gunakan add_all() untuk menambahkan multiple objek
        session.add_all(scc_configs)
        print("SCC configurations created successfully")

        # Create Tenants
        tenants = [
            Tenant(
                tenant_number=1,
                tenant_name='Tenant Utama',
                power=500,
                autonomus_day=3,
                operation_date=datetime.now(),
                install_date=datetime.now()
            ),
            Tenant(
                tenant_number=2,
                tenant_name='Tenant Cadangan',
                power=300,
                autonomus_day=2,
                operation_date=datetime.now(),
                install_date=datetime.now()
            )
        ]
        # Gunakan add_all() untuk menambahkan multiple objek
        session.add_all(tenants)
        print("Tenants created successfully")

        # Create Alarm Thresholds
        alarm_thresholds = [
            AlarmThreshold(
                tenant_id=1,
                alarm_name='Low Voltage',
                low_threshold=46.0,
                high_threshold=54.0,
                disconnect_voltage=42.0,
                reconnect_voltage=48.0
            ),
            AlarmThreshold(
                tenant_id=2,
                alarm_name='Low Voltage',
                low_threshold=46.0,
                high_threshold=54.0,
                disconnect_voltage=42.0,
                reconnect_voltage=48.0
            )
        ]
        # Gunakan add_all() untuk menambahkan multiple objek
        session.add_all(alarm_thresholds)
        print("Alarm thresholds created successfully")

        # Create LVD Settings
        lvd_settings = [
            LVDSettings(
                tenant_id=1,
                disconnect_voltage=42.0,
                reconnect_voltage=48.0,
                lvd_status='normal',
                lvd_enabled=True
            ),
            LVDSettings(
                tenant_id=2,
                disconnect_voltage=42.0,
                reconnect_voltage=48.0,
                lvd_status='normal',
                lvd_enabled=True
            )
        ]
        # Gunakan add_all() untuk menambahkan multiple objek
        session.add_all(lvd_settings)
        print("LVD settings created successfully")

        session.commit()
        print("Initial data creation completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error occurred while creating initial data: {e}")
        raise
    finally:
        session.close()

def main():
    """Main function to run migration"""
    try:
        print("Starting database migration...")
        engine = init_db()
        print("Database tables created successfully")
        
        print("Creating initial data...")
        create_initial_data(engine)
        print("Migration completed successfully")
        
    except Exception as e:
        print(f"Error occurred during migration: {e}")
        raise

if __name__ == '__main__':
    main()