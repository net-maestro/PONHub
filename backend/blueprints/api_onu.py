# -*- coding: utf-8 -*-
# api_onu.py
"""Blueprint для реєстрації ONU - Multi-OLT версія"""
from flask import Blueprint, request, jsonify, flash, get_flashed_messages
from config import olt_config
from modules.conn_to_db import db
from modules.connect import Sw_telnet
from modules.regular_expression import get_free_onu_id, replace_olt_with_onu, parse_zte_uncfg_onu, parse_zte_onu_user_mac
from jinja2 import Environment, FileSystemLoader
import os

api_onu_bp = Blueprint('api_onu', __name__, url_prefix='/netcontrol/api')

# Ініціалізація Jinja2
TEMPLATE_DIR = os.path.join(
    os.path.dirname(__file__), 
    '..', 
    'modules', 
    'onu_templates'
)
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR), 
    trim_blocks=True, 
    lstrip_blocks=True
)



def render_template(template_name: str, context: dict) -> list:
    """Рендерить Jinja2 шаблон і повертає список CLI команд"""
    template = env.get_template(template_name)
    rendered = template.render(**context)
    commands = [line.strip() for line in rendered.splitlines() if line.strip()]
    return commands

def get_free_ip_by_vlan_from_db(vlan_id):
    """Знаходить перший вільний IP по імені VLAN"""
    connection = db()
    cursor = connection.cursor()
    query = f"""
    WITH RECURSIVE ip_range AS (
        SELECT
            INET_ATON(nt.startIp) AS ip_address,
            INET_ATON(nt.stopIp) AS stop_ip,
            INET_ATON(nt.startIp) AS start_ip
        FROM eq_vlans vl
        JOIN eq_vlan_neth nv ON nv.vlan = vl.id
        JOIN eq_neth nt ON nt.id = nv.neth
        WHERE vl.vlan = '{vlan_id}'
        UNION ALL
        SELECT ip_address + 1, stop_ip, start_ip
        FROM ip_range
        WHERE ip_address + 1 <= stop_ip
    )
    SELECT INET_NTOA(ip_range.ip_address) AS free_ip
    FROM ip_range
    LEFT JOIN eq_bindings b ON INET_ATON(b.ip) = ip_range.ip_address
    WHERE b.ip IS NULL
    LIMIT 1;
    """
    try:
        cursor.execute(query)
        free_ip = cursor.fetchall()
        return free_ip
    finally:
        cursor.close()
        connection.close()

def get_olt_connection_data(olt_id=None):
    """
    Отримує дані для підключення до OLT.
    🔹 Всі дані тільки з YAML конфігурації (без дефолтів)
    """
    # 🔹 Отримуємо конкретний OLT за ID
    if olt_id is not None:
        olt = olt_config.get_olt(int(olt_id))
        if not olt:
            raise ValueError(f"OLT з ID {olt_id} не знайдено в конфігурації")
    else:
        # 🔹 Fallback: отримуємо перший enabled OLT зі списку
        all_olts = olt_config.get_all_olts()
        if not all_olts:
            raise ValueError("OLT не налаштовано в конфігурації")
        olt = next((o for o in all_olts if o.get('enabled', True)), None)
        if not olt:
            raise ValueError("Немає активних OLT в конфігурації")
    
    # 🔹 Перевірка обов'язкових полів (без дефолтів!)
    required_fields = ['ip', 'login', 'password', 'commands']
    for field in required_fields:
        if field not in olt or not olt[field]:
            raise ValueError(f"OLT не має обов'язкового поля '{field}' в конфігурації")
    
    # 🔹 Перевірка обов'язкових команд
    required_commands = ['terminal_length', 'configure', 'write']
    for cmd in required_commands:
        if cmd not in olt['commands'] or not olt['commands'][cmd]:
            raise ValueError(f"OLT не має обов'язкової команди '{cmd}' в конфігурації")
    
    return olt

# =============================================================================
# 🔹 ОТРИМАТИ ВІЛЬНИЙ IP (без змін)
# =============================================================================
@api_onu_bp.route('/get-free-ip', methods=['GET'])
def api_get_free_ip_by_vlan():
    """Отримати перший вільний IP по VLAN"""
    try:
        vlan_id = request.args.get('vlan_name')
        if not vlan_id:
            return jsonify({
                "status": "error", 
                "message": "vlan_name parameter required"
            }), 400
        
        free_ip = get_free_ip_by_vlan_from_db(vlan_id)
        
        return jsonify({
            "status": "success", 
            "free_ip": free_ip
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

# =============================================================================
# 🔹 ОТРИМАТИ ВІЛЬНИЙ ONU ID (з підтримкою olt_id)
# =============================================================================
@api_onu_bp.route('/get-free-onu', methods=['POST'])
def api_get_free_onu():
    """Отримати вільний ONU ID на порту"""
    try:
        data = request.get_json()
        interface = data.get('interface')
        olt_id = data.get('olt_id')
        
        if not interface:
            return jsonify({
                "status": "error",
                "message": "interface parameter required"
            }), 400
        
        # 🔹 Отримуємо дані підключення до OLT (тільки з конфігурації)
        olt = get_olt_connection_data(olt_id)
        
        # 🔹 Отримуємо команди та defaults з конфігурації
        commands = olt['commands']
        defaults = olt_config.get_defaults()
        max_id = defaults.get('max_onu_id', 128)
        
        # 🔹 Формуємо команди для Telnet (тільки з конфігурації)
        telnet_commands = [
            commands['terminal_length'], 
            commands['configure'],
            f"{commands.get('show_running_interface', commands.get('show_running'))} {interface}"
        ]
        
        last_onu = Sw_telnet(
            olt['ip'], 
            olt.get('timeout', 5), 
            olt['login'], 
            olt['password'],
            telnet_commands
        )
        config_output = last_onu.get_result()
        
        if not config_output:
            raise RuntimeError(f"Не вдалося отримати конфігурацію порту {interface}")
        
        free_onu_id = get_free_onu_id(config_output, max_id)
        flash(f"Вільний ONU ID для {interface}: {free_onu_id}", 'info')
        messages = get_flashed_messages(with_categories=True)
        
        return jsonify({
            "status": "success",
            "onuId": free_onu_id,
            "messages": messages,
            "olt_id": olt_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 400

# =============================================================================
# 🔹 ПРЕДПРОСМОТР КОНФІГУРАЦІЇ (з підтримкою olt_id)
# =============================================================================
@api_onu_bp.route('/preview-onu-config', methods=['POST'])
def api_preview_onu_config():
    """
    Генерує конфиг для ONU, але НЕ застосовує його.
    Повертає config для попереднього перегляду + валідацію вхідних даних.
    """
    config_str = ""
    try:
        data = request.get_json()
        
        # 🔹 Валідація обов'язкових полів
        required_fields = ['interface', 'onuId', 'onuType', 'speed', 'vlan', 'sn']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Відсутні поля: {', '.join(missing)}",
                "config": None,
                "validation_errors": missing
            }), 400
        
        interface = data.get('interface')
        onu_id_val = data.get('onuId')
        speed = data.get('speed')
        onu_type = data.get('onuType')
        vlan = data.get('vlan')
        comment = data.get('comment', '')
        sn = data.get('sn')
        olt_id = data.get('olt_id')
        
        # 🔹 Перевірка OLT (якщо вказано olt_id)
        if olt_id:
            get_olt_connection_data(olt_id)
        
        # 🔹 Парсинг VLAN: "profileKey+++vlanId"
        if '+++' not in str(vlan):
            return jsonify({
                "status": "error",
                "message": "Невірний формат VLAN. Очікується: 'profile+++id'",
                "config": None
            }), 400
            
        vlan_name, vlan_id = vlan.split('+++')
        
        # 🔹 Додаткові перевірки
        try:
            onu_id_val = int(onu_id_val)
            speed_val = int(str(speed).replace('mb', '').replace('M', ''))
            if not (1 <= onu_id_val <= 128):
                raise ValueError("ONU ID має бути 1-128")
        except (ValueError, TypeError) as e:
            return jsonify({
                "status": "error",
                "message": f"Помилка в числових параметрах: {str(e)}",
                "config": None
            }), 400
        
        # 🔹 Генерація конфига (БЕЗ виконання!)
        port_onu_name = replace_olt_with_onu(interface)
        template_name = f"zte_{onu_type.lower()}.j2"
        
        context = {
            "port_name": interface,
            "onu_id": onu_id_val,
            "onu_type": onu_type,
            "sn_onu": sn,
            "speed": str(speed_val),
            "vlan_name": vlan_name,
            "vlan_id": vlan_id,
            "port_onu_name": port_onu_name,
            "comment": comment,
        }
        
        config_commands = render_template(template_name, context)
        config_str = "\n".join(config_commands)
        
        # 🔹 Аналіз конфига для UI
        config_analysis = {
            "commands_count": len(config_commands),
            "estimated_execution_time": f"~{len(config_commands) * 0.3:.1f} сек",
            "sections": {
                "registration": any("onu " in cmd.lower() for cmd in config_commands),
                "vlan_config": any("vlan" in cmd.lower() for cmd in config_commands),
                "security": any("security" in cmd.lower() for cmd in config_commands),
                "service_port": any("service-port" in cmd.lower() for cmd in config_commands),
            }
        }
        
        return jsonify({
            "status": "preview",
            "message": "Конфіг згенеровано. Перевірте та підтвердіть застосування.",
            "config": config_str,
            "config_analysis": config_analysis,
            "payload_summary": {
                "olt_id": olt_id,
                "interface": interface,
                "onu_id": onu_id_val,
                "onu_type": onu_type,
                "sn": sn,
                "vlan": f"{vlan_name} ({vlan_id})",
                "speed": f"{speed_val} Mbps"
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Помилка генерації конфіга: {str(e)}",
            "config": config_str,
            "error_type": type(e).__name__
        }), 500

# =============================================================================
# 🔹 РЕЄСТРАЦІЯ ONU (з підтримкою olt_id)
# =============================================================================
@api_onu_bp.route('/register-onu', methods=['POST'])
def api_register_onu():
    """Реєстрація ONU на OLT"""
    config_str = ""
    try:
        data = request.get_json()
        interface = data.get('interface')
        onu_id_val = data.get('onuId')
        speed = data.get('speed')
        onu_type = data.get('onuType')
        vlan = data.get('vlan')
        comment = data.get('comment')
        sn = data.get('sn')
        olt_id = data.get('olt_id')
        
        # 🔹 Отримуємо дані підключення до OLT (тільки з конфігурації)
        olt = get_olt_connection_data(olt_id)
        
        # 🔹 Парсинг VLAN
        if '+++' not in str(vlan):
            raise ValueError("Невірний формат VLAN")
        vlan_name, vlan_id = vlan.split('+++')
        
        # 🔹 Генерація конфига
        port_onu_name = replace_olt_with_onu(interface)
        template_name = f"zte_{onu_type.lower()}.j2"
        
        context = {
            "port_name": interface,
            "onu_id": onu_id_val,
            "onu_type": onu_type,
            "sn_onu": sn,
            "speed": str(speed).replace('mb', '').replace('M', ''),
            "vlan_name": vlan_name,
            "vlan_id": vlan_id,
            "port_onu_name": port_onu_name,
            "comment": comment,
        }
        
        config_commands = render_template(template_name, context)
        config_str = "\n".join(config_commands)
        
        # 🔹 Виконуємо реальну реєстрацію
        commands = olt['commands']
        
        # 🔹 Додаємо команду write з конфігурації (не дефолт!)
        config_commands.append(commands['write'])
        
        Sw_telnet(
            olt['ip'], 
            olt.get('timeout', 5), 
            olt['login'], 
            olt['password'], 
            config_commands
        )
        
        flash(f"ONU SN:{sn} зареєстровано {interface}:{onu_id_val}", 'success')
        messages = get_flashed_messages(with_categories=True)
        
        return jsonify({
            "status": "success",
            "messages": messages,
            "config": config_str,
            "applied_commands_count": len(config_commands),
            "olt_id": olt_id
        }), 200
        
    except Exception as e:
        flash(f"ПОМИЛКА: {str(e)}", 'danger')
        messages = get_flashed_messages(with_categories=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "messages": messages,
            "config": config_str,
            "config_generated": bool(config_str)
        }), 400

# =============================================================================
# 🔹 SHOW UNCONFIGURED ONU (з підтримкою olt_id)
# =============================================================================
@api_onu_bp.route('/show-uncfg-onu', methods=['GET'])
def api_show_uncfg_onu():
    """Показати незареєстровані ONU"""
    try:
        olt_id = request.args.get('olt_id')
        
        # 🔹 Отримуємо дані підключення до OLT (тільки з конфігурації)
        olt = get_olt_connection_data(olt_id)
        
        commands = olt['commands']
        
        # 🔹 Використовуємо команду з конфігурації (show_uncfg або show_uncfg_onu)
        show_uncfg_cmd = commands.get('show_uncfg') or commands.get('show_uncfg_onu')
        if not show_uncfg_cmd:
            raise ValueError("Команда 'show_uncfg' не налаштована в конфігурації OLT")
        
        last_onu = Sw_telnet(
            olt['ip'], 
            olt.get('timeout', 5), 
            olt['login'], 
            olt['password'],
            [
                commands['terminal_length'],
                show_uncfg_cmd
            ]
        )
        config_output = parse_zte_uncfg_onu(last_onu.get_result())

        line = '''
         OltIndex            Model                SN                 PW
         -----------------------------------------------------------------------------
         gpon_olt-1/1/15     PU-X910              HWTCAF48ED18       1234567890
         gpon_olt-1/1/16     PU-X910              ZTEGC1234567       1234567890
         gpon_olt-1/1/17     PU-X910              HWTCABCD9876       1234567890 
               '''

        #config_output = parse_zte_uncfg_onu(line)      

        
        if not config_output:
            config_output = "Немає незареєстрованих ONU"


        return jsonify({
            "status": "success",
            "data": config_output,
            "olt_id": olt_id
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

# =============================================================================
# 🔹 SHOW MAC INTERFACE gpon_onu-1/1/1:1
# =============================================================================
@api_onu_bp.route('/get-onu-user-mac', methods=['GET'])
def api_get_onu_user_mac():
    """Отримати MAC-адресу роутера за ONU
    api/get-onu-user-mac?olt_id=1&interface=gpon-onu_1/1/1:1
    """
    try:
        olt_id = request.args.get('olt_id')
        interface = request.args.get('interface')
        
        if not olt_id or not interface:
            return jsonify({
                "status": "error",
                "message": "Необхідні параметри: olt_id та interface"
            }), 400
        
        # 🔹 Отримуємо дані підключення до OLT
        olt = get_olt_connection_data(olt_id)
        
        commands = olt['commands']
        
        # 🔹 Використовуємо команду з конфігурації (show_mac_onu)
        show_mac_cmd = commands.get('show_onu_user_mac')
        if not show_mac_cmd:
            raise ValueError("Команда 'show_onu_user_mac' не налаштована в конфігурації OLT")
        
        # 🔹 Форматуємо команду з interface
        # Приклад: show mac interface gpon_onu-1/1/1:1
        formatted_cmd = f"{show_mac_cmd} {interface}"
        print(formatted_cmd)
        
        last_onu = Sw_telnet(
            olt['ip'], 
            olt.get('timeout', 5), 
            olt['login'], 
            olt['password'],
            [
                commands['terminal_length'],
                formatted_cmd
            ]
        )
        
        config_output = last_onu.get_result()
        
        # 🔹 Парсимо MAC-адресу з виводу
        mac_address = parse_zte_onu_user_mac(config_output)
        
        if not mac_address:
            mac_address = None
            message = "MAC-адресу не знайдено"
        else:
            message = "MAC-адресу успішно отримано"

        return jsonify({
            "status": "success",
            "mac_address": mac_address,
            "message": message,
            "interface": interface,
            "olt_id": olt_id,
            "raw_output": config_output  # 🔹 Опціонально: сирий вивід для дебагу
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400