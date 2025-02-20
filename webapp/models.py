from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class SiteData(Base):
    __tablename__ = 'site_data'
    
    id = Column(Integer, primary_key=True)
    site_id = Column(String(100))
    site_name = Column(String(100))
    address = Column(Text)
    ip_address = Column(String(50))
    net_mask = Column(String(50))
    gateway = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

class BMSData(Base):
    __tablename__ = 'bms_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    bms_number = Column(Integer, nullable=False)
    communication = Column(Boolean)
    serial_number = Column(String(100))
    brand = Column(String(100))
    voltage = Column(Float)
    current = Column(Float)
    remain_capacity = Column(Float)
    capacity = Column(Float)
    soc = Column(Float)
    soh = Column(Float)
    ambient_temperature = Column(Float)
    mos_temperature = Column(Float)
    communication_smartli = Column(Boolean)
    serial_number_smartli = Column(String(100))
    current_smartli = Column(Float)
    voltage_smartli = Column(Float)
    soc_smartli = Column(Float)
    soh_smartli = Column(Float)
    capacity_smartli = Column(Float)
    battery_stolen_status = Column(Boolean, default=False)
    battery_stolen_alarm = Column(Boolean, default=False)
    
    cell_voltages = relationship("CellVoltage", back_populates="bms", cascade="all, delete-orphan")

class BMSConfig(Base):
    __tablename__ = 'bms_config'
    
    id = Column(Integer, primary_key=True)
    vendor_name = Column(String(100), nullable=False)
    battery_type = Column(String(100), nullable=False)
    num_of_pack = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

class SCCData(Base):
    __tablename__ = 'scc_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    scc_number = Column(Integer, nullable=False)
    voltage_pv = Column(Float)
    current_pv = Column(Float)
    power_pv = Column(Float)
    voltage_scc = Column(Float)
    current_scc = Column(Float)
    power_scc = Column(Float)
    temperature_pv = Column(Float)
    temperature_scc = Column(Float)
    is_active = Column(Boolean, default=False)
    ip_address = Column(String(50))
    modbus_address = Column(String(50))

class SCCConfig(Base):
    __tablename__ = 'scc_config'
    
    id = Column(Integer, primary_key=True)
    scc_number = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=False)
    ip_address = Column(String(50))
    modbus_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

class CalibrationData(Base):
    __tablename__ = 'calibration_data'
    
    id = Column(Integer, primary_key=True)
    parameter = Column(String(50), nullable=False)
    real_parameter = Column(Float)
    scale_vector = Column(Float)
    input_scale = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

class AlarmThreshold(Base):
    __tablename__ = 'alarm_thresholds'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete="CASCADE"))
    alarm_name = Column(String(50), nullable=False)
    low_threshold = Column(Float)
    high_threshold = Column(Float)
    disconnect_voltage = Column(Float)
    reconnect_voltage = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

    tenant = relationship("Tenant")

class TenantCalibrationData(Base):
    __tablename__ = 'tenant_calibration_data'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete="CASCADE"))
    parameter = Column(String(50))
    real_parameter = Column(Float)
    scale_vector = Column(Float)
    input_scale = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())
    
    tenant = relationship("Tenant", back_populates="calibration_data")

class LVDSettings(Base):
    __tablename__ = 'lvd_settings'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete="CASCADE"))
    disconnect_voltage = Column(Float)
    reconnect_voltage = Column(Float)
    lvd_status = Column(String(20))
    lvd_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

    tenant = relationship("Tenant", back_populates="lvd_settings")

class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    tenant_number = Column(Integer, nullable=False)
    tenant_name = Column(String(100), nullable=False)
    power = Column(Float)
    autonomus_day = Column(Integer)
    operation_date = Column(DateTime)
    install_date = Column(DateTime)
    device_upgrades = Column(String(255))
    update_date = Column(DateTime)
    
    load_data = relationship("LoadData", back_populates="tenant", cascade="all, delete-orphan")
    lvd_settings = relationship("LVDSettings", back_populates="tenant", cascade="all, delete-orphan")
    calibration_data = relationship("TenantCalibrationData", back_populates="tenant", cascade="all, delete-orphan")

class LoadData(Base):
    __tablename__ = 'load_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete="CASCADE"), nullable=False)
    dcpd_status = Column(Boolean, default=False)
    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)

    tenant = relationship("Tenant", back_populates="load_data")

class EnvironmentData(Base):
    __tablename__ = 'environment_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float)
    temperature_status = Column(Integer)
    humidity_status = Column(Integer)
    door_status = Column(Integer)
    door_alarm = Column(Integer)

class DeviceInfo(Base):
    __tablename__ = 'device_info'
    
    id = Column(Integer, primary_key=True)
    serial_number = Column(String(100), unique=True)
    device_model = Column(String(100))
    part_number = Column(String(100))
    software_ver = Column(String(50))
    hardware_ver = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())

class CellVoltage(Base):
    __tablename__ = 'cell_voltages'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    bms_id = Column(Integer, ForeignKey('bms_data.id', ondelete="CASCADE"), nullable=False)
    cell_number = Column(Integer, nullable=False)
    voltage = Column(Float)
    
    bms = relationship("BMSData", back_populates="cell_voltages")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    level = Column(Enum('admin', 'operator', 'viewer', name='user_level'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())