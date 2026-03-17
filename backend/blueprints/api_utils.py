# -*- coding: utf-8 -*-
# api_utils.py
"""Blueprint для утилит и конфигурации"""

from flask import Blueprint, jsonify
from config import olt_config

api_utils_bp = Blueprint(
    'api_utils',
    __name__,
    url_prefix='/netcontrol/api'
)


# -----------------------------------------------------
# HEALTH CHECK
# -----------------------------------------------------

@api_utils_bp.route('/', methods=['GET'])
def api_health_check():
    """Заглушка перевірки доступності API можливо додати ping OLT"""
    return jsonify({
        "status": "ok",
        "message": "API работает"
    }), 200


# -----------------------------------------------------
# ВСЕ OLT
# -----------------------------------------------------

@api_utils_bp.route('/device/config', methods=['GET'])
def api_get_all_devices_config():
    """Отримати конфігурацію всіх OLT"""

    try:
        olts = olt_config.get_all_olts()
        defaults = olt_config.get_defaults()

        result = []

        for olt in olts:
            olt_id = olt.get('id')

            result.append({
                "oltId": olt_id,
                "deviceName": olt.get('name', 'ZTE'),
                "deviceIp": olt.get('ip', ''),
                "enabled": olt.get('enabled', True),
                "interfaces": olt_config.get_interfaces(olt_id),
                "onuTypes": olt_config.get_onu_types(olt_id),
                "speeds": olt_config.get_speeds(olt_id),
                "vlans": olt_config.get_vlans(olt_id),
                "portVlanMapping": olt_config.get_port_vlan_mapping(olt_id),
                "defaults": defaults,
                "activeOnuCount": 12  # можешь заменить реальным методом позже
            })

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# -----------------------------------------------------
# КОНКРЕТНЫЙ OLT
# -----------------------------------------------------

@api_utils_bp.route('/device/config/<int:olt_id>', methods=['GET'])
def api_get_single_device_config(olt_id):
    """Отримати конфігурацію OLT по olt_id"""

    try:
        olt = olt_config.get_olt(olt_id)

        if not olt:
            return jsonify({
                "success": False,
                "error": "OLT не найден"
            }), 404

        defaults = olt_config.get_defaults()

        return jsonify({
            "success": True,
            "data": {
                "oltId": olt_id,
                "deviceName": olt.get('name', 'ZTE'),
                "deviceIp": olt.get('ip', ''),
                "enabled": olt.get('enabled', True),
                "interfaces": olt_config.get_interfaces(olt_id),
                "onuTypes": olt_config.get_onu_types(olt_id),
                "speeds": olt_config.get_speeds(olt_id),
                "vlans": olt_config.get_vlans(olt_id),
                "portVlanMapping": olt_config.get_port_vlan_mapping(olt_id),
                "defaults": defaults,
                "activeOnuCount": 12
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500