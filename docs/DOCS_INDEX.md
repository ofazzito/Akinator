# 📚 Documentación del Proyecto Akinator

## 📋 Índice de Documentos

### Documentación Principal
- **[README.md](../README.md)** - Inicio rápido y características principales (en raíz)
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Guía completa de Docker
- **[DOCKER_COMPLETE.md](DOCKER_COMPLETE.md)** - Resumen de dockerización completada

### Documentación Técnica
- **[AI_EXPANSION.md](AI_EXPANSION.md)** - Sistema de expansión con IA
- **[BATCH_SYSTEM.md](BATCH_SYSTEM.md)** - Procesamiento batch asíncrono
- **[MULTI_SOURCE.md](MULTI_SOURCE.md)** - Integración de múltiples fuentes de datos
- **[ANALISIS_PROYECTO.md](ANALISIS_PROYECTO.md)** - Análisis técnico completo

---

## 🎯 Guía Rápida por Objetivo

### Quiero empezar a usar el proyecto
👉 Lee [README.md](../README.md) - Sección "Inicio Rápido"

### Quiero usar Docker
👉 Lee [DOCKER_SETUP.md](DOCKER_SETUP.md) - Guía completa paso a paso

### Quiero expandir la base de datos con IA
👉 Lee [AI_EXPANSION.md](AI_EXPANSION.md) - Sistema de expansión automática

### Quiero importar muchos personajes rápidamente
👉 Lee [BATCH_SYSTEM.md](BATCH_SYSTEM.md) - Procesamiento paralelo

### Quiero entender la arquitectura del proyecto
👉 Lee [ANALISIS_PROYECTO.md](ANALISIS_PROYECTO.md) - Análisis completo

---

## 📦 Stack Tecnológico Actual

### Backend
- **Python:** 3.13
- **Framework:** Flask 3.0.0
- **ORM:** SQLAlchemy 3.1.1
- **Base de datos:** PostgreSQL 17 (Docker) / SQLite (local)
- **Driver PostgreSQL:** Psycopg3
- **Caché:** Redis 7
- **IA:** OpenAI GPT-4o-mini + DALL-E 3

### Frontend
- **HTML5 + CSS3 + JavaScript** (Vanilla)
- **Diseño:** Glassmorphism
- **Responsive:** Sí

### Infraestructura
- **Contenedores:** Docker
- **Orquestación:** Docker Compose
- **Gestor de paquetes:** UV (desarrollo) / pip (local)
- **Reverse Proxy:** Nginx (producción)
- **Servidor:** Gunicorn + Gevent (producción)

---

## 🗂️ Estructura de Archivos

```
Akinator/
├── backend/                    # Código Python
│   ├── app.py                 # Aplicación Flask principal
│   ├── models.py              # Modelos SQLAlchemy
│   ├── game_engine.py         # Lógica del juego
│   ├── learning_system.py     # Sistema de aprendizaje
│   ├── ai_expansion.py        # Expansión con IA
│   ├── batch_processor.py     # Procesamiento batch
│   └── ...
├── static/                     # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                  # Templates HTML
│   └── index.html
├── Dockerfile                  # Imagen Docker desarrollo
├── Dockerfile.prod            # Imagen Docker producción
├── docker-compose.yml         # Orquestación desarrollo
├── docker-compose.prod.yml    # Orquestación producción
├── requirements.txt           # Dependencias Python
├── requirements-prod.txt      # Dependencias producción
└── *.md                       # Documentación
```

---

## 🚀 Comandos Rápidos

### Docker (Recomendado)
```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Detener
docker-compose down

# Rebuild
docker-compose build
```

### Local
```bash
# Activar entorno
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Iniciar app
python backend/app.py
```

---

## 📝 Documentos Eliminados (Obsoletos)

Los siguientes documentos fueron eliminados por estar obsoletos:
- ~~CHANGELOG_PYTHON_3.14.md~~ - Historial de cambios de versión (ya no relevante)
- ~~DOCKER_OPTIONS.md~~ - Análisis de opciones (decisión ya tomada)
- ~~FLASK_VS_FASTAPI.md~~ - Comparación de frameworks (decisión tomada: Flask)

---

## 🔄 Última Actualización

**Fecha:** 2026-01-07  
**Versión:** 1.0.0  
**Estado:** Producción Ready

**Cambios recientes:**
- ✅ Dockerización completa
- ✅ PostgreSQL 17 como base de datos
- ✅ Python 3.13 + UV
- ✅ Psycopg3 driver moderno
- ✅ Documentación actualizada y consolidada
