# Dockerfile para Akinator Clone
# Multi-stage build para optimizar tamaño de imagen

# ===== STAGE 1: Builder =====
FROM python:3.13-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (gestor de paquetes ultrarrápido)
RUN pip install --no-cache-dir uv

# Copiar requirements y instalar dependencias con uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# ===== STAGE 2: Runtime =====
FROM python:3.13-slim

# Metadata
LABEL maintainer="tu-email@ejemplo.com"
LABEL description="Akinator Clone - Juego de adivinanzas con IA"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=backend/app.py \
    FLASK_ENV=production

# Instalar dependencias de runtime para PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 akinator && \
    mkdir -p /app && \
    chown -R akinator:akinator /app

WORKDIR /app

# Copiar dependencias desde builder (uv instala en /usr/local con --system)
COPY --from=builder /usr/local /usr/local

# Copiar código de la aplicación
COPY --chown=akinator:akinator . .

# Copiar y dar permisos al script de inicio
COPY --chown=akinator:akinator docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Crear directorios necesarios
RUN mkdir -p /app/backend/static/images/characters && \
    chown -R akinator:akinator /app

# Cambiar a usuario no-root
USER akinator

# Exponer puerto
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/stats')" || exit 1

# Comando por defecto (desarrollo)
CMD ["/app/docker-entrypoint.sh"]
