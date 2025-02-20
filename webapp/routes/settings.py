from flask import (
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    current_app
)
from sqlalchemy.orm import Session
from models import SiteData, DeviceInfo, User, Tenant, BMSConfig, SCCConfig
import json
import os

settings_bp = Blueprint('settings', __name__)

def get_db_session():
    """Get database session from current app context"""
    return current_app.db_session

@settings_bp.route('/scc/settings')
def scc_settings():
    """Route for Solar Charge Controller (SCC) settings"""
    try:
        session = get_db_session()
        scc_list = session.query(SCCConfig).all()
        return render_template('scc_setting.html', scc_list=scc_list)
    except Exception as e:
        print(f"Error getting SCC settings: {e}")
        return render_template('scc_setting.html', scc_list=[])

@settings_bp.route('/scc/save', methods=['POST'])
def save_scc():
    """Save SCC configuration"""
    try:
        data = request.get_json()
        session = get_db_session()
        
        # Get SCC number and find existing config or create new
        scc_number = data.get('scc_number')
        scc = session.query(SCCConfig).filter_by(scc_number=scc_number).first()
        if not scc:
            scc = SCCConfig(scc_number=scc_number)
            session.add(scc)
        
        # Update configuration
        scc.is_active = data.get('is_active', False)
        scc.ip_address = data.get('ip_address')
        scc.modbus_address = data.get('modbus_address')
        
        session.commit()
        return jsonify({
            'success': True, 
            'message': 'SCC settings saved successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 400

@settings_bp.route('/scc/delete/<int:scc_number>', methods=['POST'])
def delete_scc(scc_number):
    try:
        session = get_db_session()
        scc = session.query(SCCConfig).filter_by(scc_number=scc_number).first()
        
        if scc:
            session.delete(scc)
            session.commit()
            return jsonify({
                'success': True,
                'message': f'SCC {scc_number} deleted successfully'
            })
        return jsonify({
            'success': False,
            'message': f'SCC {scc_number} not found'
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@settings_bp.route('/bms/settings')
def bms_settings():
    """Route for Battery Monitoring System (BMS) settings"""
    try:
        session = get_db_session()
        config = session.query(BMSConfig).first()
        
        if not config:
            bms_config = {
                'vendor_name': 'PT. Sundaya Indonesia',
                'battery_type': 'Talis 30',
                'num_of_pack': 1
            }
        else:
            bms_config = {
                'vendor_name': config.vendor_name,
                'battery_type': config.battery_type,
                'num_of_pack': config.num_of_pack
            }
        
        vendors = ['PT. Sundaya Indonesia', 'Other Vendor']
        battery_types = ['Talis 30', 'Other Battery Type']
        
        return render_template('bms_setting.html',
                             config=bms_config,
                             vendors=vendors,
                             battery_types=battery_types)
    except Exception as e:
        print(f"Error getting BMS settings: {e}")
        return render_template('bms_setting.html',
                             config={},
                             vendors=[],
                             battery_types=[])

@settings_bp.route('/bms/save', methods=['POST'])
def save_bms():
    """Save BMS configuration"""
    try:
        session = get_db_session()
        
        # Get form data
        vendor_name = request.form.get('vendor_name')
        battery_type = request.form.get('battery_type')
        pack_count = request.form.get('packCount')
        
        # Find existing config or create new
        config = session.query(BMSConfig).first()
        if not config:
            config = BMSConfig()
            session.add(config)
        
        # Update configuration
        config.vendor_name = vendor_name
        config.battery_type = battery_type
        config.num_of_pack = int(pack_count)
        
        session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'BMS settings saved successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 400

# Existing routes remain unchanged
@settings_bp.route('/user/config')
def user_config():
    return render_template('user_config.html')

@settings_bp.route('/site/config')
def site_config():
    return render_template('site_tenant_config.html')

@settings_bp.route('/site/data', methods=['GET'])
def get_site_data():
    try:
        session = get_db_session()
        site = session.query(SiteData).first()
        tenants = session.query(Tenant).all()
        
        return jsonify({
            'site': {
                'site_id': site.site_id if site else '',
                'site_name': site.site_name if site else '',
                'address': site.address if site else '',
                'ip_address': site.ip_address if site else '',
                'net_mask': site.net_mask if site else '',
                'updated_at': site.updated_at if site else None
            },
            'tenants': [
                {
                    'id': tenant.id,
                    'tenant_name': tenant.tenant_name,
                    'power': tenant.power,
                    'autonomus_day': tenant.autonomus_day,
                    'operation_date': tenant.operation_date,
                    'device_upgrades': tenant.device_upgrades,
                    'update_date': tenant.update_date
                } for tenant in tenants
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': str(e)
        }), 400

# Add these routes to your settings_bp Blueprint

@settings_bp.route('/pms/settings')
def device_settings():
    """Route for Device Info settings"""
    try:
        session = get_db_session()
        device = session.query(DeviceInfo).first()
        return render_template('pms_setting.html', device=device)
    except Exception as e:
        print(f"Error getting device settings: {e}")
        return render_template('pms_setting.html', device=None)

@settings_bp.route('/device/save', methods=['POST'])
def save_device():
    """Save device configuration"""
    try:
        session = get_db_session()
        
        # Get existing device or create new one
        device = session.query(DeviceInfo).first()
        if not device:
            device = DeviceInfo()
            session.add(device)
        
        # Update device information
        device.device_model = request.form.get('device_model')
        device.part_number = request.form.get('part_number')
        device.serial_number = request.form.get('serial_number')
        device.software_ver = request.form.get('software_ver')
        device.hardware_ver = request.form.get('hardware_ver')
        
        session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device settings saved successfully'
        })
    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
# Remaining routes for site/tenant management remain unchanged