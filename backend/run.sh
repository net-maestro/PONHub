#!/usr/bin/env bash

echo "🚀 Запуск ONU Registration System..."

cd /home/vivaldi/netcontrol/backend || exit 1
source env/bin/activate

echo "🔧 Запуск Flask API..."
exec python3 app.py