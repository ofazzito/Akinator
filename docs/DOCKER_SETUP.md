# 🐳 Guía de Dockerización - Akinator Clone

## 📋 Contenido

1. [Requisitos](#requisitos)
2. [Inicio Rápido](#inicio-rápido)
3. [Desarrollo](#desarrollo)
4. [Producción](#producción)
5. [Comandos Útiles](#comandos-útiles)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git** (para clonar el repositorio)
- **Python 3.13** (en las imágenes Docker)
- **PostgreSQL 17** (en contenedor)

### Instalación de Docker

#### Windows
```bash
# Descargar Docker Desktop
https://www.docker.com/products/docker-desktop/

# Verificar instalación
docker --version
docker-compose --version
```

#### Linux
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Descargar Docker Desktop
https://www.docker.com/products/docker-desktop/
```

---

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.docker .env

# Editar .env y configurar:
# - OPENAI_API_KEY (opcional pero recomendado)
# - Contraseñas de PostgreSQL y Redis
```

### 2. Levantar servicios

```bash
# Desarrollo (con hot reload)
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

### 3. Acceder a la aplicación

- **Aplicación:** http://localhost:5000
- **PgAdmin:** http://localhost:5050 (opcional)
- **Redis Commander:** http://localhost:8081 (opcional)

---

## 💻 Desarrollo

### Arquitectura de Servicios

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│                                         │
│  ┌──────────┐  ┌──────────┐            │
│  │   App    │  │PostgreSQL│            │
│  │  Flask   │──│   DB     │            │
│  │  :5000   │  │  :5432   │            │
│  └──────────┘  └──────────┘            │
│       │                                 │
│       │        ┌──────────┐            │
│       └────────│  Redis   │            │
│                │  :6379   │            │
│                └──────────┘            │
└─────────────────────────────────────────┘
```

### Comandos de Desarrollo

#### Iniciar servicios
```bash
# Todos los servicios
docker-compose up -d

# Solo servicios principales (sin PgAdmin/Redis Commander)
docker-compose up -d app db redis

# Con herramientas de desarrollo
docker-compose --profile dev-tools up -d
```

#### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo app
docker-compose logs -f app

# Últimas 100 líneas
docker-compose logs --tail=100 app
```

#### Ejecutar comandos en contenedor
```bash
# Shell interactivo
docker-compose exec app bash

# Ejecutar script de expansión
docker-compose exec app python backend/expand_database.py

# Verificar base de datos
docker-compose exec app python verify_db.py

# Acceder a PostgreSQL
docker-compose exec db psql -U akinator -d akinator
```

#### Reiniciar servicios
```bash
# Reiniciar app
docker-compose restart app

# Reiniciar todos
docker-compose restart
```

#### Detener servicios
```bash
# Detener sin eliminar
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Eliminar también volúmenes (¡CUIDADO! Borra datos)
docker-compose down -v
```

### Hot Reload

El código en `backend/`, `static/` y `templates/` está montado como volumen, por lo que **los cambios se reflejan automáticamente** sin reiniciar el contenedor.

```yaml
volumes:
  - ./backend:/app/backend      # Hot reload ✅
  - ./static:/app/static        # Hot reload ✅
  - ./templates:/app/templates  # Hot reload ✅
```

### Acceder a PgAdmin

1. Abrir http://localhost:5050
2. Login:
   - Email: `admin@akinator.local`
   - Password: `admin`
3. Agregar servidor:
   - Host: `db`
   - Port: `5432`
   - Database: `akinator`
   - Username: `akinator`
   - Password: (el configurado en `.env`)

### Acceder a Redis Commander

1. Abrir http://localhost:8081
2. Explorar claves de Redis
3. Ver caché y sesiones

---

## 🏭 Producción

### 1. Configurar variables de entorno

```bash
# Crear .env para producción
cp .env.docker .env

# Configurar valores seguros:
SECRET_KEY=tu-clave-super-secreta-aleatoria-aqui
POSTGRES_PASSWORD=contraseña-fuerte-postgresql
REDIS_PASSWORD=contraseña-fuerte-redis
OPENAI_API_KEY=sk-tu-api-key
```

### 2. Build de imagen de producción

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Build sin caché
docker-compose -f docker-compose.prod.yml build --no-cache
```

### 3. Levantar en producción

```bash
# Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Acceder a la aplicación

- **Aplicación:** http://localhost:80
- **API:** http://localhost:80/api/stats

### Diferencias Desarrollo vs Producción

| Aspecto | Desarrollo | Producción |
|---------|-----------|------------|
| **Servidor** | Flask dev server | Gunicorn + 4 workers |
| **Puerto** | 5000 | 8000 (interno), 80 (Nginx) |
| **Debug** | Activado | Desactivado |
| **Hot Reload** | Sí | No |
| **Volúmenes código** | Montados | Copiados en imagen |
| **Nginx** | No | Sí (reverse proxy) |
| **Herramientas dev** | PgAdmin, Redis Commander | No |

---

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Ver contenedores activos
docker-compose ps

# Ver uso de recursos
docker stats

# Inspeccionar contenedor
docker inspect akinator_app

# Ver redes
docker network ls
```

### Gestión de Volúmenes

```bash
# Listar volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect akinator_postgres_data

# Backup de PostgreSQL
docker-compose exec db pg_dump -U akinator akinator > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U akinator akinator < backup.sql
```

### Limpieza

```bash
# Eliminar contenedores detenidos
docker-compose down

# Eliminar imágenes sin usar
docker image prune -a

# Eliminar volúmenes sin usar
docker volume prune

# Limpieza completa (¡CUIDADO!)
docker system prune -a --volumes
```

### Debugging

```bash
# Shell en contenedor app
docker-compose exec app bash

# Ver variables de entorno
docker-compose exec app env

# Probar conexión a PostgreSQL
docker-compose exec app python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://akinator:akinator_password_change_me@db:5432/akinator'); print(engine.connect())"

# Probar conexión a Redis
docker-compose exec app python -c "import redis; r = redis.Redis(host='redis', port=6379, password='redis_password_change_me', decode_responses=True); print(r.ping())"
```

---

## 🔧 Troubleshooting

### Problema: Puerto ya en uso

```bash
# Error: Bind for 0.0.0.0:5000 failed: port is already allocated

# Solución 1: Cambiar puerto en docker-compose.yml
ports:
  - "5001:5000"  # Usar 5001 en lugar de 5000

# Solución 2: Detener proceso que usa el puerto
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs app

# Ver últimos errores
docker-compose logs --tail=50 app

# Reiniciar contenedor
docker-compose restart app

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Ver logs de PostgreSQL
docker-compose logs db

# Probar conexión manual
docker-compose exec db psql -U akinator -d akinator

# Verificar healthcheck
docker inspect akinator_db | grep -A 10 Health
```

### Problema: Cambios no se reflejan

```bash
# Verificar volúmenes montados
docker-compose exec app ls -la /app/backend

# Reiniciar app
docker-compose restart app

# Si persiste, rebuild
docker-compose down
docker-compose up -d --build
```

### Problema: Permisos en Windows

```bash
# Error: Permission denied

# Solución: Asegurar que Docker Desktop tenga acceso a la carpeta
# Settings → Resources → File Sharing → Agregar carpeta del proyecto
```

---

## 📊 Migración desde SQLite a PostgreSQL

### 1. Exportar datos de SQLite

```bash
# Desde SQLite
python -c "
from backend.models import db, Character, Question
import json

# Exportar personajes
characters = Character.query.all()
with open('characters.json', 'w') as f:
    json.dump([c.to_dict() for c in characters], f)

# Exportar preguntas
questions = Question.query.all()
with open('questions.json', 'w') as f:
    json.dump([q.to_dict() for q in questions], f)
"
```

### 2. Importar a PostgreSQL

```bash
# Dentro del contenedor
docker-compose exec app python -c "
from backend.models import db, Character, Question
import json

# Crear tablas
db.create_all()

# Importar personajes
with open('characters.json') as f:
    characters = json.load(f)
    for c in characters:
        # Crear personaje...
"
```

---

## 🎯 Próximos Pasos

Una vez dockerizado, puedes:

1. **Implementar migraciones** con Alembic
2. **Agregar CI/CD** con GitHub Actions
3. **Deploy en cloud** (AWS, GCP, Azure)
4. **Configurar Nginx** para SSL/HTTPS
5. **Implementar monitoreo** con Prometheus

---

## 📚 Recursos

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

---

**¡Tu proyecto Akinator ahora está completamente dockerizado!** 🎉
