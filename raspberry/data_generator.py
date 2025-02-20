from datetime import datetime
import random
import json
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import SiteData, DeviceInfo, BMSConfig, SCCConfig, Tenant

class DataGenerator:
    def __init__(self, db_url):
        self.host = "192.168.3.59"
        # Setup database connection
        self.engine = create_engine(db_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def get_bms_config(self):
        """Get latest BMS configuration from database"""
        try:
            # Ambil konfigurasi BMS terbaru berdasarkan tanggal update
            config = self.session.query(BMSConfig).order_by(BMSConfig.updated_at.desc()).first()
            if config:
                return {
                    'vendor_name': config.vendor_name,
                    'battery_type': config.battery_type,
                    'num_of_pack': config.num_of_pack
                }
        except Exception as e:
            print(f"Error getting BMS config: {e}")
        return {}

    def get_scc_config(self):
        """Get latest SCC configurations from database"""
        try:
            # Ambil semua konfigurasi SCC, diurutkan dari yang terbaru
            configs = self.session.query(SCCConfig).order_by(SCCConfig.updated_at.desc()).all()
            return {scc.scc_number: {
                'is_active': scc.is_active,
                'ip_address': scc.ip_address,
                'modbus_address': scc.modbus_address
            } for scc in configs}
        except Exception as e:
            print(f"Error getting SCC config: {e}")
        return {}

    def generate_site_data(self):
        """Generate site data"""
        try:
            site = self.session.query(SiteData).first()
            if site:
                site_data = [
                    {"key": "asset.site_id", "val": site.site_id},
                    {"key": "asset.site_name", "val": site.site_name},
                    {"key": "asset.address", "val": site.address},
                    {"key": "asset.ip_address", "val": site.ip_address},
                    {"key": "asset.net_mask", "val": site.net_mask},
                    {"key": "asset.gateway", "val": site.gateway}
                ]
                return site_data
        except Exception as e:
            print(f"Error getting site data: {e}")
        return []

    def generate_device_data(self):
        """Generate device info data"""
        try:
            device = self.session.query(DeviceInfo).first()
            if device:
                device_data = [
                    {"key": "asset.device_model", "val": device.device_model},
                    {"key": "asset.serial_number", "val": device.serial_number},
                    {"key": "asset.part_number", "val": device.part_number},
                    {"key": "asset.software_ver", "val": device.software_ver},
                    {"key": "asset.hardware_ver", "val": device.hardware_ver}
                ]
                return device_data
        except Exception as e:
            print(f"Error getting device data: {e}")
        return []
    
    def generate_tenant_data(self):
        """Generate tenant data"""
        try:
            # Query all tenants
            tenants = self.session.query(Tenant).all()
            
            tenant_data_list = []
            for tenant in tenants:
                tenant_data = [
                    {"key": f"asset.tenant{tenant.tenant_number}_id", "val": str(tenant.id)},
                    {"key": f"asset.tenant{tenant.tenant_number}_name", "val": tenant.tenant_name},
                    {"key": f"asset.tenant{tenant.tenant_number}_power", "val": str(tenant.power)},
                    {"key": f"asset.tenant{tenant.tenant_number}_autonomus_day", "val": str(tenant.autonomus_day)},
                    {"key": f"asset.tenant{tenant.tenant_number}_operation_date", "val": tenant.operation_date.isoformat() if tenant.operation_date else ""},
                    {"key": f"asset.tenant{tenant.tenant_number}_install_date", "val": tenant.install_date.isoformat() if tenant.install_date else ""},
                    {"key": f"asset.tenant{tenant.tenant_number}_device_upgrades", "val": tenant.device_upgrades or ""},
                    {"key": f"asset.tenant{tenant.tenant_number}_update_date", "val": tenant.update_date.isoformat() if tenant.update_date else ""}
                ]
                
                tenant_data_list.extend(tenant_data)
            
            return tenant_data_list
        except Exception as e:
            print(f"Error generating tenant data: {e}")
            return []
        
    def generate_load_data(self):
        """Generate load data for all existing tenants"""
        try:
            # Query all tenants
            tenants = self.session.query(Tenant).all()
            
            load_data_list = []
            for tenant in tenants:
                # Generate random load data for each tenant
                load_data = {
                    f"load.data.dcpdb_tenant{tenant.tenant_number}": str(random.choice([0, 1])),
                    f"load.data.volt_tenant{tenant.tenant_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"load.data.curr_tenant{tenant.tenant_number}": str(round(random.uniform(0.0, 8.0), 2)),
                    f"load.data.power_tenant{tenant.tenant_number}": str(round(random.uniform(0.0, tenant.power or 432.0), 2))
                }
                
                load_data_list.extend([
                    {"key": key, "val": value} for key, value in load_data.items()
                ])
            
            return load_data_list
        except Exception as e:
            print(f"Error generating load data: {e}")
            return []
        
    def generate_bms_data(self):
        """Generate random BMS data for all BMS packs"""
        try:
            config = self.get_bms_config()
            if not config:
                return []
                
            bms_data_list = []
            num_of_pack = config.get('num_of_pack', 1)
            
            for bms_number in range(1, num_of_pack + 1):
                # Generate BMS general data
                base_bms_data = {
                    f"battery_bank.data.com_bms{bms_number}": str(random.choice([1])),
                    f"battery_bank.data.sn_bms{bms_number}": str(round(random.uniform(1000, 2000), 2)),
                    f"battery_bank.data.brand_bms{bms_number}": config.get('vendor_name', 'Undefined'),
                    f"battery_bank.data.battery_type_bms{bms_number}": config.get('battery_type', 'Undefined'),
                    f"battery_bank.data.volt_bms{bms_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"battery_bank.data.curr_bms{bms_number}": str(round(random.uniform(0.0, 90.0), 2)),
                    f"battery_bank.data.rem_capacity_bms{bms_number}": str(round(random.uniform(50.0, 100.0), 2)),
                    f"battery_bank.data.capacity_bms{bms_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"battery_bank.data.soc_bms{bms_number}": str(round(random.uniform(0.0, 100.0), 2)),
                    f"battery_bank.data.soh_bms{bms_number}": str(round(random.uniform(80.0, 100.0), 2)),
                    f"battery_bank.data.amb_temp_bms{bms_number}": str(round(random.uniform(28.0, 60.0), 2)),
                    f"battery_bank.data.mos_temp_bms{bms_number}": str(round(random.uniform(28.0, 60.0), 2)),
                    f"battery_bank.data.com_smart-li{bms_number}": str(random.choice([0, 1])),
                    f"battery_bank.data.sn_smart-li{bms_number}": str(round(random.uniform(1000, 2000), 2)),
                    f"battery_bank.data.curr_smart-li{bms_number}": str(round(random.uniform(0.0, 90.0), 2)),
                    f"battery_bank.data.volt_smart-li{bms_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"battery_bank.data.soc_smart-li{bms_number}": str(round(random.uniform(0.0, 100.0), 2)),
                    f"battery_bank.data.soh_smart-li{bms_number}": str(round(random.uniform(80.0, 100.0), 2)),
                    f"battery_bank.data.capacity_smart-li{bms_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"digital_input.data.batt_stolen{bms_number}": str(random.choice([0, 1, 2])),
                    f"digital_input.data.batt_stolen_alarm{bms_number}": str(random.choice([0, 1, 2, 3]))
                }
                
                # Convert base_bms_data to list format
                bms_data_list.extend([
                    {"key": key, "val": value} for key, value in base_bms_data.items()
                ])
                
                # Generate cell voltages
                for cell_number in range(1, 15):
                    bms_data_list.append({
                        "key": f"battery_bank.cell{cell_number}_volt_bms{bms_number}",
                        "val": str(round(random.uniform(2.9, 3.4), 2))
                    })
            
            return bms_data_list
            
        except Exception as e:
            print(f"Error generating BMS data: {e}")
            return []

    def generate_scc_data(self):
        """Generate random SCC data for all active SCCs"""
        try:
            scc_configs = self.get_scc_config()
            if not scc_configs:
                return []
            
            scc_data_list = []
            for scc_number, scc_config in scc_configs.items():
                # Only generate data for active SCCs
                if not scc_config['is_active']:
                    continue
                
                # SCC data generation
                scc_data_detail = {
                    f"pv_module.data.is_active_scc{scc_number}": str(scc_config['is_active']),
                    f"pv_module.data.ip_address_scc{scc_number}": scc_config.get('ip_address', f'192.168.3.{60+scc_number}'),
                    f"pv_module.data.modbus_address_scc{scc_number}": scc_config.get('modbus_address', str(scc_number)),
                    f"pv_module.data.volt_pv{scc_number}": str(round(random.uniform(30.0, 80.0), 2)),
                    f"pv_module.data.curr_pv{scc_number}": str(round(random.uniform(0.0, 40.0), 2)),
                    f"pv_module.data.power_pv{scc_number}": str(round(random.uniform(0.0, 3200.0), 2)),
                    f"pv_module.data.volt_scc{scc_number}": str(round(random.uniform(46.0, 54.0), 2)),
                    f"pv_module.data.curr_scc{scc_number}": str(round(random.uniform(0.0, 20.0), 2)),
                    f"pv_module.data.power_scc{scc_number}": str(round(random.uniform(0.0, 1080.0), 2)),
                    f"pv_module.data.temp_pv{scc_number}": str(round(random.uniform(25.0, 60.0), 2)),
                    f"pv_module.data.temp_scc{scc_number}": str(round(random.uniform(25.0, 60.0), 2))
                }
                
                # Convert to list format
                scc_data_list.extend([
                    {"key": key, "val": value} for key, value in scc_data_detail.items()
                ])
            
            return scc_data_list
            
        except Exception as e:
            print(f"Error generating SCC data: {e}")
            return []

    def generate_environment_data(self):
        """Generate environment data"""
        env_data = [
            {"key": "environment.data.temp_rack", "val": str(round(random.uniform(20.0, 35.0), 2))},
            {"key": "environment.data.hum_rack", "val": str(round(random.uniform(40.0, 70.0), 2))},
            {"key": "environment_alarm.data.temp_rack_status", "val": str(random.choice([0, 1, 2, 3, 4, 5]))},
            {"key": "environment_alarm.data.hum_rack_status", "val": str(random.choice([0, 1, 2, 3, 4, 5]))},
            {"key": "digital_input.data.door_cabinet", "val": str(random.choice([0, 1, 2]))},
            {"key": "digital_input.data.door_cabinet_alarm", "val": str(random.choice([0, 1, 2, 3]))}
        ]
        return env_data

    def generate_data(self):
        """Generate all sensor data"""
        try:
            timestamp = datetime.now()
            
            consolidated_message = {
                "ts": int(timestamp.timestamp() * 1e9),
                "host": self.host,
                "data": []
            }

            # Tambahkan data dari setiap metode generate
            consolidated_message["data"].extend(self.generate_site_data())
            consolidated_message["data"].extend(self.generate_device_data())
            consolidated_message["data"].extend(self.generate_tenant_data())
            consolidated_message["data"].extend(self.generate_load_data())
            consolidated_message["data"].extend(self.generate_bms_data())
            consolidated_message["data"].extend(self.generate_scc_data())
            consolidated_message["data"].extend(self.generate_environment_data())

            return consolidated_message, timestamp
            
        except Exception as e:
            print(f"Error generating data: {e}")
            return None, None

    def cleanup(self):
        """Close database session"""
        self.session.close()
