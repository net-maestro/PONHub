# -*- coding: utf-8 -*-
"""Модуль загрузки конфигурации OLT из YAML"""
import os
import yaml
import threading


class OLTConfig:
    """Загрузка и управление конфигурацией OLT с авто-перезагрузкой"""

    def __init__(self):
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            'otls_config.yaml'
        )
        self._lock = threading.Lock()
        self._last_mtime = None
        self.config = {}
        self._load_config()

    def _load_config(self):
        """Загружает YAML конфигурацию"""
        with self._lock:
            if not os.path.exists(self.config_path):
                self.config = {}
                return

            mtime = os.path.getmtime(self.config_path)

            if self._last_mtime == mtime:
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}

            self._last_mtime = mtime
            print("🔄 OLT config reloaded")

    def _ensure_updated(self):
        """Проверяет и обновляет конфигурацию при необходимости"""
        self._load_config()

    # ----------------------------------------------------
    # ОСНОВНОЙ МЕТОД
    # ----------------------------------------------------

    def get_olt(self, olt_id=None):
        """
        Если указан olt_id → вернуть конкретный OLT
        Если None → вернуть список всех OLT
        """
        self._ensure_updated()
        olts = self.config.get('olts', [])

        if olt_id is not None:
            for olt in olts:
                if olt.get('id') == olt_id:
                    return olt
            return None

        return olts

    def get_all_olts(self):
        self._ensure_updated()
        return self.config.get('olts', [])

    def get_defaults(self):
        self._ensure_updated()
        return self.config.get('defaults', {})

    # ----------------------------------------------------
    # ДАННЫЕ ПО OLT
    # ----------------------------------------------------

    def get_onu_types(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            olt = self.get_olt(olt_id)
            return olt.get('onu_types', {}) if olt else {}

        result = {}
        for olt in self.get_olt():
            result[olt['id']] = olt.get('onu_types', {})
        return result

    def get_speeds(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            olt = self.get_olt(olt_id)
            return olt.get('speeds', []) if olt else []

        result = {}
        for olt in self.get_olt():
            result[olt['id']] = olt.get('speeds', [])
        return result

    def get_vlans(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            olt = self.get_olt(olt_id)
            return olt.get('vlans', {}) if olt else {}

        result = {}
        for olt in self.get_olt():
            result[olt['id']] = olt.get('vlans', {})
        return result

    def get_port_vlan_mapping(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            olt = self.get_olt(olt_id)
            return olt.get('port_vlan_mapping', {}) if olt else {}

        result = {}
        for olt in self.get_olt():
            result[olt['id']] = olt.get('port_vlan_mapping', {})
        return result

    def get_interfaces(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            mapping = self.get_port_vlan_mapping(olt_id)
            return list(mapping.keys())

        result = {}
        for olt_id, mapping in self.get_port_vlan_mapping().items():
            result[olt_id] = list(mapping.keys())
        return result

    def get_commands(self, olt_id=None):
        self._ensure_updated()

        if olt_id is not None:
            olt = self.get_olt(olt_id)
            return olt.get('commands', {}) if olt else {}

        result = {}
        for olt in self.get_olt():
            result[olt['id']] = olt.get('commands', {})
        return result


# Глобальный экземпляр
olt_config = OLTConfig()