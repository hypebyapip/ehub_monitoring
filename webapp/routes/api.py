# from flask import Blueprint, jsonify, current_app

# api_bp = Blueprint('api', __name__, url_prefix='/api')

# @api_bp.route('/monitoring/battery')
# def get_battery_data():
#     """Get latest battery monitoring data"""
#     return jsonify(current_app.mqtt_client.get_battery_data())

# @api_bp.route('/monitoring/scc')
# def get_scc_data():
#     """Get latest SCC monitoring data"""
#     return jsonify(current_app.mqtt_client.get_scc_data())

# @api_bp.route('/monitoring/history')
# def get_history_data():
#     """Get historical monitoring data"""
#     return jsonify(current_app.mqtt_client.get_history_data())