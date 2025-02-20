from flask import Blueprint, render_template, jsonify, current_app
from sqlalchemy.orm import Session
from models import SCCConfig

monitoring_bp = Blueprint('monitoring', __name__)

def get_db_session():
    """Get database session from current app context"""
    return current_app.db_session

@monitoring_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@monitoring_bp.route('/monitoring/battery')
def battery_monitoring():
    return render_template('battery.html')

@monitoring_bp.route('/monitoring/scc')
def scc_monitoring():
    try:
        session = get_db_session()
        active_scc = session.query(SCCConfig).filter_by(is_active=True).order_by(SCCConfig.scc_number).all()
        return render_template('scc.html', scc_list=active_scc)
    except Exception as e:
        print(f"Error getting active SCC list: {e}")
        return render_template('scc.html', scc_list=[])

@monitoring_bp.route('/monitoring/load')
def load_monitoring():
    return render_template('load.html')

@monitoring_bp.route('/api/monitoring/scc')
def get_scc_data():
    """Get latest SCC monitoring data"""
    try:
        session = get_db_session()
        active_scc = session.query(SCCConfig).filter_by(is_active=True).all()
        active_scc_numbers = [scc.scc_number for scc in active_scc]
        
        data = current_app.mqtt_client.get_latest_data()
        if not data['data']:
            return jsonify({
                'status': 'error',
                'message': 'No data available'
            }), 404

        # Process SCC data - only for active SCCs
        scc_data = {}
        total_pv_power = 0
        total_scc_power = 0

        for item in data['data']:
            key = item['key']
            if 'pv_module' in key:
                # Extract SCC number from key (assuming format like "pv_module.data.XXX.N")
                scc_num = int(key[-1])
                
                # Only process data for active SCCs
                if scc_num in active_scc_numbers:
                    scc_data[key] = item['val']
                    
                    # Calculate totals
                    if 'power_pv' in key:
                        total_pv_power += float(item['val'])
                    elif 'power_scc' in key:
                        total_scc_power += float(item['val'])

        # Calculate system efficiency
        system_efficiency = (total_scc_power / total_pv_power * 100) if total_pv_power > 0 else 0

        return jsonify({
            'status': 'success',
            'timestamp': data['ts'],
            'host': data['host'],
            'data': scc_data,
            'summary': {
                'total_pv_power': total_pv_power,
                'total_scc_power': total_scc_power,
                'system_efficiency': round(system_efficiency, 2)
            },
            'active_scc': active_scc_numbers
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/monitoring/battery')
def get_battery_data():
    """Get latest battery monitoring data"""
    try:
        data = current_app.mqtt_client.get_latest_data()
        if not data['data']:
            return jsonify({
                'status': 'error',
                'message': 'No data available'
            }), 404

        # Process battery data
        battery_data = {}
        for item in data['data']:
            key = item['key']
            if 'battery_bank' in key or 'batt_stolen' in key:
                battery_data[key] = item['val']

        return jsonify({
            'status': 'success',
            'timestamp': data['ts'],
            'host': data['host'],
            'data': battery_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@monitoring_bp.route('/api/monitoring/history')
def get_history_data():
    """Get historical monitoring data"""
    return jsonify(current_app.mqtt_client.get_history_data())