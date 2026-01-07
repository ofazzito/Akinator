#!/bin/bash
# Script de inicio para Docker
# Este script inicializa la base de datos y luego inicia la aplicación

echo "🚀 Iniciando Akinator..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a PostgreSQL..."
while ! python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///backend/database.db')); engine.connect()" 2>/dev/null; do
    sleep 1
done
echo "✅ PostgreSQL listo"

# Inicializar base de datos
echo "📊 Inicializando base de datos..."
python backend/init_db_docker.py

# Iniciar aplicación
echo "🎮 Iniciando aplicación Flask..."
exec python backend/app.py
