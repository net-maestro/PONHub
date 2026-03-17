# -*- coding: utf-8 -*-
"""Модуль подключения к базе данных биллинга"""
import os
import pymysql.cursors
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_IP = os.getenv('DB_IP')
DB_USER = os.getenv('DB_LOGIN')
DB_PASSWD = os.getenv('DB_PASSWD')
DB_NAME = os.getenv('DB_NAME')

def db():
    """Returns a database connection."""
    return pymysql.connect(
        host=DB_IP,
        user=DB_USER,
        password=DB_PASSWD,
        database=DB_NAME,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )