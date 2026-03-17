# -*- coding: utf-8 -*-
"""Модуль вспомогательных функций"""
import re


def convert_cisco_mac_to_standard(cisco_mac):
    """
    Конвертація MAC з формату Cisco (7820.5120.9b20) в стандартний (78:20:51:20:9b:20)
    
    Args:
        cisco_mac: MAC у форматі Cisco (xxxx.xxxx.xxxx)
    Returns:
        MAC у стандартному форматі (xx:xx:xx:xx:xx:xx)
    """
    # 🔹 Видаляємо крапки та робимо lowercase
    mac_clean = cisco_mac.replace('.', '').lower()
    
    # 🔹 Додаємо двокрапки кожні 2 символи
    mac_standard = ':'.join(mac_clean[i:i+2] for i in range(0, 12, 2))
    
    return mac_standard


def parse_zte_onu_user_mac(output):
    """
    Парсинг MAC-адреси з виводу команди show mac interface
    
    Приклад виводу:
    ZTE#show mac interface gpon_onu-1/1/1:1
    Total mac address : 1

    Mac address      Vlan  Type      Port                     Vc                                 
    -------------------------------------------------------------------------------
    7820.5120.9b20   1101   Dynamic   vport-1/1/1.1:1
    
    Повертає: 78:20:51:20:9b:20
    """
    if not output:
        return None
    
    try:
        lines = output.strip().split('\n')
        
        # 🔹 Шукаємо рядок з MAC-адресою (після роздільника)
        mac_pattern = re.compile(r'^([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+', re.MULTILINE)
        
        for line in lines:
            match = mac_pattern.match(line.strip())
            if match:
                # 🔹 Конвертуємо з формату Cisco (7820.5120.9b20) в стандартний (78:20:51:20:9b:20)
                mac_cisco = match.group(1)
                mac_standard = convert_cisco_mac_to_standard(mac_cisco).upper()
                return mac_standard
        
        return None
        
    except Exception as e:
        print(f"Error parsing MAC: {e}")
        return None







def parse_zte_uncfg_onu(cli_output: str):
    """
    Универсальный парсер для:
      - show pon onu uncfg (C600/C620)
      - show gpon onu uncfg (C320)

    Возвращает:
    [
        {"port": "1/2/5", "sn": "ZTEGC1684EEF"},
        ...
    ]
    """

    result = []

    # --- C320 формат ---
    # gpon-onu_1/2/5:1   ZTEGC1684EEF   unknown
    pattern_c320 = re.compile(
        r'gpon-onu_(\d+/\d+/\d+):\d+\s+([A-Z0-9]{8,20})',
        re.IGNORECASE
    )

    # --- C600/C620 формат ---
    # gpon_olt-1/1/15    MODEL    HWTCAF48ED18
    pattern_c600 = re.compile(
        r'gpon_olt-(\d+/\d+/\d+)\s+\S+\s+([A-Z0-9]{8,20})',
        re.IGNORECASE
    )

    # ищем C320
    for match in pattern_c320.finditer(cli_output):
        result.append({
            "port": match.group(1),
            "sn": match.group(2)
        })

    # ищем C600
    for match in pattern_c600.finditer(cli_output):
        result.append({
            "port": match.group(1),
            "sn": match.group(2)
        })

    return result

    

def get_occupied_onu_ids(config_lines):
    """Извлекает ВСЕ занятые ID ONU из конфигурации порта."""
    matches = re.findall(r'\s+onu\s+(\d+)\s+', config_lines)
    occupied = set()
    for match in matches:
        try:
            onu_id = int(match)
            if 1 <= onu_id <= 128:
                occupied.add(onu_id)
        except ValueError:
            continue
    return occupied

def find_first_free_onu_id(occupied_ids, max_id=128):
    """Находит ПЕРВЫЙ свободный ID в диапазоне 1..max_id."""
    occupied_set = set(occupied_ids)
    for onu_id in range(1, max_id + 1):
        if onu_id not in occupied_set:
            return onu_id
    return None

def get_free_onu_id(config_output, max_id=128):
    """Основная функция: получает свободный ID ONU из вывода конфигурации."""
    occupied = get_occupied_onu_ids(config_output)
    free_id = find_first_free_onu_id(occupied, max_id)
    if free_id is None:
        raise RuntimeError(f"Порт переполнен! Все 128 слотов заняты.")
    return free_id

def replace_olt_with_onu(input_string):
    """Заменяет olt на onu в имени интерфейса"""
    return input_string.replace('olt', 'onu')