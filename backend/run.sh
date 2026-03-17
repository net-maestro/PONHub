#!/usr/bin/env bash

echo "🚀 Запуск ONU Registration System..."

cd /PONHub/backend || exit 1
source env/bin/activate

echo "🔧 Запуск Flask API..."
exec python3 app.py
