# -*- coding: utf-8 -*-
"""Модуль подключения к OLT по Telnet"""
import time
import telnetlib

class Sw_telnet:
    def __init__(self, host, timeout, login, password, sw_command):
        self.host = host
        self.timeout = int(timeout)
        self.login = login
        self.password = password
        self.sw_command = sw_command
        self.output = None
        self.__sw()
    
    def to_bytes(self, line):
        return f"{line}\r\n".encode("utf-8")
    
    def __sw(self):
        try:
            with telnetlib.Telnet(self.host, timeout=self.timeout) as tn:
                tn.write(self.to_bytes(self.login))
                tn.write(self.to_bytes(self.password))
                for command in self.sw_command:
                    tn.write(self.to_bytes(command))
                    time.sleep(0.5)
                time.sleep(self.timeout)
                self.output = tn.read_very_eager().decode("utf-8")
        except Exception as e:
            self.output = None
            self.error = f"Failed to connect to {self.host}: {str(e)}"
    
    def get_result(self):
        return self.output
    
    def print_result(self):
        if self.output:
            print(f"Output from {self.host}:\n{self.output}")
        else:
            print(getattr(self, "error", f"No output from {self.host}"))