from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models
from models import (
    SiteData, BMSData, SCCData, CalibrationData, 
    AlarmThreshold, TenantCalibrationData, LVDSettings,
    Tenant, LoadData, EnvironmentData, DeviceInfo,
    CellVoltage, User
)

class DatabaseHandler:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def save_bms_data(self, bms_data, timestamp):
        """Save BMS data and associated cell voltages"""
        with self.session_scope() as session:
            for bms_number, data in bms_data.items():
                db_bms = BMSData(
                    timestamp=timestamp,
                    bms_number=bms_number,
                    communication=bool(int(data.get(f'battery_bank.data.com_bms{bms_number}', 0))),
                    serial_number=str(data.get(f'battery_bank.data.sn_bms{bms_number}', '')),
                    brand=data.get(f'battery_bank.data.brand_bms{bms_number}', ''),
                    voltage=float(data.get(f'battery_bank.data.volt_bms{bms_number}', 0)),
                    current=float(data.get(f'battery_bank.data.curr_bms{bms_number}', 0)),
                    remain_capacity=float(data.get(f'battery_bank.data.rem_capacity_bms{bms_number}', 0)),
                    capacity=float(data.get(f'battery_bank.data.capacity_bms{bms_number}', 0)),
                    soc=float(data.get(f'battery_bank.data.soc_bms{bms_number}', 0)),
                    soh=float(data.get(f'battery_bank.data.soh_bms{bms_number}', 0)),
                    ambient_temperature=float(data.get(f'battery_bank.data.amb_temp_bms{bms_number}', 0)),
                    mos_temperature=float(data.get(f'battery_bank.data.mos_temp_bms{bms_number}', 0)),
                    communication_smartli=bool(int(data.get(f'battery_bank.data.com_smart-li{bms_number}', 0))),
                    serial_number_smartli=str(data.get(f'battery_bank.data.sn_smart-li{bms_number}', '')),
                    current_smartli=float(data.get(f'battery_bank.data.curr_smart-li{bms_number}', 0)),
                    voltage_smartli=float(data.get(f'battery_bank.data.volt_smart-li{bms_number}', 0)),
                    soc_smartli=float(data.get(f'battery_bank.data.soc_smart-li{bms_number}', 0)),
                    soh_smartli=float(data.get(f'battery_bank.data.soh_smart-li{bms_number}', 0)),
                    capacity_smartli=float(data.get(f'battery_bank.data.capacity_smart-li{bms_number}', 0)),
                    battery_stolen_status=bool(int(data.get(f'digital_input.data.batt_stolen{bms_number}', 0))),
                    battery_stolen_alarm=bool(int(data.get(f'digital_input.data.batt_stolen_alarm{bms_number}', 0)))
                )
                session.add(db_bms)
                session.flush()  # To get the ID of the newly created BMS record

                # Simpan voltase sel
                for cell_number in range(1, 15):
                    cell_voltage = CellVoltage(
                        timestamp=timestamp,
                        bms_id=db_bms.id,
                        cell_number=cell_number,
                        voltage=float(data.get(f'battery_bank.cell{cell_number}_volt_bms{bms_number}', 0))
                    )
                    session.add(cell_voltage)

    def save_scc_data(self, scc_data, timestamp):
        """Save SCC (Solar Charge Controller) data"""
        with self.session_scope() as session:
            for scc_number, data in scc_data.items():
                db_scc = SCCData(
                    timestamp=timestamp,
                    scc_number=scc_number,
                    voltage_pv=float(data.get(f'pv_module.data.volt_pv{scc_number}', 0)),
                    current_pv=float(data.get(f'pv_module.data.curr_pv{scc_number}', 0)),
                    power_pv=float(data.get(f'pv_module.data.power_pv{scc_number}', 0)),
                    voltage_scc=float(data.get(f'pv_module.data.volt_scc{scc_number}', 0)),
                    current_scc=float(data.get(f'pv_module.data.curr_scc{scc_number}', 0)),
                    power_scc=float(data.get(f'pv_module.data.power_scc{scc_number}', 0)),
                    temperature_pv=float(data.get(f'pv_module.data.temp_pv{scc_number}', 0)),
                    temperature_scc=float(data.get(f'pv_module.data.temp_scc{scc_number}', 0)),
                    is_active=bool(data.get(f'pv_module.data.is_active_scc{scc_number}', False)),
                    ip_address=data.get(f'pv_module.data.ip_address_scc{scc_number}', ''),
                    modbus_address=data.get(f'pv_module.data.modbus_address_scc{scc_number}', '')
                )
                session.add(db_scc)

    def save_environment_data(self, env_data, timestamp):
        """Save environment data"""
        with self.session_scope() as session:
            db_env = EnvironmentData(
                timestamp=timestamp,
                temperature=float(env_data.get('environment.data.temp_rack', 0)),
                humidity=float(env_data.get('environment.data.hum_rack', 0)),
                temperature_status=int(env_data.get('environment_alarm.data.temp_rack_status', 0)),
                humidity_status=int(env_data.get('environment_alarm.data.hum_rack_status', 0)),
                door_status=int(env_data.get('digital_input.data.door_cabinet', 0)),
                door_alarm=int(env_data.get('digital_input.data.door_cabinet_alarm', 0))
            )
            session.add(db_env)

    def save_load_data(self, load_data, timestamp):
        """Save load data for existing tenants"""
        with self.session_scope() as session:
            for tenant_number, data in load_data.items():
                # Cari tenant yang sudah ada
                tenant = session.query(Tenant).filter_by(tenant_number=tenant_number).first()
                if tenant:
                    # Buat record load data
                    load_entry = LoadData(
                        timestamp=timestamp,
                        tenant_id=tenant.id,
                        dcpd_status=bool(int(data.get(f'load.data.dcpdb_tenant{tenant_number}', 0))),
                        voltage=float(data.get(f'load.data.volt_tenant{tenant_number}', 0)),
                        current=float(data.get(f'load.data.curr_tenant{tenant_number}', 0)),
                        power=float(data.get(f'load.data.power_tenant{tenant_number}', 0))
                    )
                    session.add(load_entry)

    def save_all_data(self, data):
        """Save all sensor data"""
        timestamp = datetime.fromtimestamp(data['ts'] / 1e9)
        
        try:
            # Parsing data
            bms_data = {}
            scc_data = {}
            env_data = {}
            tenant_load_data = {}
            
            for item in data['data']:
                key = item['key']
                value = item['val']
                
                # Parsing data berdasarkan jenis
                if key.startswith('load.data'):
                    parts = key.split('_')
                    tenant_number = int(parts[-1].replace('tenant', ''))
                    
                    if tenant_number not in tenant_load_data:
                        tenant_load_data[tenant_number] = {}
                    
                    tenant_load_data[tenant_number][key] = value
                
                elif 'battery_bank' in key or 'batt_stolen' in key:
                    # Parsing BMS
                    bms_number = int(key[-1]) if key[-1].isdigit() else 1
                    
                    if bms_number not in bms_data:
                        bms_data[bms_number] = {}
                    
                    bms_data[bms_number][key] = value
                
                elif 'pv_module' in key:
                    # Parsing SCC
                    scc_number = int(key[-1]) if key[-1].isdigit() else 1
                    
                    if scc_number not in scc_data:
                        scc_data[scc_number] = {}
                    
                    scc_data[scc_number][key] = value
                
                elif any(x in key for x in ['environment', 'door_cabinet']):
                    # Parsing lingkungan
                    env_data[key] = value
            
            # Simpan data
            if tenant_load_data:
                self.save_load_data(tenant_load_data, timestamp)
            
            if bms_data:
                self.save_bms_data(bms_data, timestamp)
            
            if scc_data:
                self.save_scc_data(scc_data, timestamp)
            
            if env_data:
                self.save_environment_data(env_data, timestamp)
                    
        except Exception as e:
            print(f"Error saving data to database: {e}")
            raise