# ============================================
# Quick Go - Script de Creación de Proyecto
# Autor: Cristian - UPEC
# PowerShell Script para Windows
# Versión: 2.0 - Corregida para carpeta existente
# ============================================

Write-Host "========================================" -ForegroundColor Blue
Write-Host "   QUICK GO - PROYECTO SETUP" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

Write-Host "Creando estructura en carpeta actual..." -ForegroundColor Green
Write-Host "Ubicación: $((Get-Location).Path)" -ForegroundColor Yellow
Write-Host ""

# Verificar si ya hay archivos
$files = Get-ChildItem -Path . -File | Where-Object { $_.Name -ne "Setup-QuickGo.ps1" -and $_.Name -ne "Create-QuickGoProject.ps1" -and $_.Name -ne ".gitignore" -and $_.Name -ne "README.md" }
if ($files.Count -gt 0) {
    Write-Host "⚠ Ya existen algunos archivos en esta carpeta" -ForegroundColor Yellow
    $response = Read-Host "¿Continuar de todas formas? (s/n)"
    if ($response -ne "s" -and $response -ne "S") {
        Write-Host "Instalación cancelada" -ForegroundColor Red
        exit
    }
}

# ============================================
# FUNCIÓN AUXILIAR
# ============================================
function Create-FileWithContent {
    param(
        [string]$Path,
        [string]$Content
    )
    $dir = Split-Path -Path $Path -Parent
    if ($dir -and !(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $Path -Value $Content -Encoding UTF8
}

# ============================================
# 1. ARCHIVOS RAÍZ
# ============================================
Write-Host "[1/7] Creando archivos raíz..." -ForegroundColor Cyan

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
env/
venv/
ENV/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
*.log

# Django
*.sqlite3
db.sqlite3
media/
staticfiles/
static_root/

# Environment
.env
.env.local
*.env

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
*.tgz

# React Native
.expo/
.expo-shared/
ios/Pods/
android/.gradle/
android/app/build/
*.jks
*.p8
*.p12
*.key
*.mobileprovision

# Next.js
.next/
out/
build/
dist/

# Docker
*.log

# Carpeta generada por script anterior
quick-go/
"@

Create-FileWithContent -Path ".gitignore" -Content $gitignoreContent

$envExampleContent = @"
# Django Settings
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-12345678901234567890
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
DB_NAME=quickgo_db
DB_USER=quickgo_user
DB_PASSWORD=quickgo_password_2024
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# API URLs
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000

# JWT
JWT_SECRET_KEY=jwt-secret-key-change-this-12345678901234567890
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
"@

Create-FileWithContent -Path ".env.example" -Content $envExampleContent

$readmeContent = @"
# Quick Go - Aplicación de Delivery

Sistema completo de delivery con panel de administración web y aplicaciones móviles.

## 🚀 Tecnologías

- **Backend**: Django + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Panel Admin**: Next.js + TypeScript
- **Apps Móviles**: React Native + TypeScript
- **Containerización**: Docker + Docker Compose

## 📁 Estructura del Proyecto

``````
quickgo/
├── backend/           # API Django REST Framework
├── admin-web/         # Panel administrativo (Next.js)
├── mobile-customer/   # App móvil para clientes
└── mobile-driver/     # App móvil para repartidores
``````

## 🛠️ Instalación y Configuración

### Requisitos Previos

- Docker Desktop para Windows
- Node.js 18+ y npm
- Visual Studio Code
- Android Studio (opcional, para desarrollo móvil)

### 1. Configuración Inicial

``````powershell
# Copiar archivo de variables de entorno
Copy-Item .env.example .env

# Editar .env con tus configuraciones
code .env
``````

### 2. Levantar Backend con Docker

``````powershell
# Construir y levantar contenedores
docker-compose up --build

# En otra terminal PowerShell, ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
``````

### 3. Panel de Administración Web

``````powershell
cd admin-web
npm install
npm run dev
``````

Acceder a: http://localhost:3000

### 4. App Móvil - Clientes

``````powershell
cd mobile-customer
npm install
npm run android
``````

### 5. App Móvil - Repartidores

``````powershell
cd mobile-driver
npm install
npm run android
``````

## 📱 Accesos

- **API Backend**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Panel Web Admin**: http://localhost:3000
- **API Documentation**: http://localhost:8000/swagger

## 👥 Tipos de Usuarios

1. **Administrador**: Gestión completa del sistema (web)
2. **Cliente**: Realizar y rastrear pedidos (móvil)
3. **Repartidor**: Aceptar y entregar pedidos (móvil)

## 🔧 Comandos Útiles (PowerShell)

``````powershell
# Ver logs del backend
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Detener todos los servicios
docker-compose down

# Limpiar volúmenes (cuidado: borra la BD)
docker-compose down -v
``````

## 📝 Desarrollo

### Backend (Django)

``````powershell
# Crear nueva app
docker-compose exec backend python manage.py startapp nombre_app

# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Shell de Django
docker-compose exec backend python manage.py shell
``````

## 👨‍💻 Autor

Desarrollado por Cristian - UPEC
Universidad Politécnica Estatal del Carchi
"@

Create-FileWithContent -Path "README.md" -Content $readmeContent

$dockerComposeContent = @"
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: quickgo_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=`${DB_NAME}
      - POSTGRES_USER=`${DB_USER}
      - POSTGRES_PASSWORD=`${DB_PASSWORD}
    ports:
      - "5432:5432"
    networks:
      - quickgo_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U `${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    container_name: quickgo_backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    environment:
      - DEBUG=`${DEBUG}
      - SECRET_KEY=`${SECRET_KEY}
      - DB_NAME=`${DB_NAME}
      - DB_USER=`${DB_USER}
      - DB_PASSWORD=`${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=`${REDIS_URL}
    depends_on:
      db:
        condition: service_healthy
    networks:
      - quickgo_network

  admin-web:
    build: ./admin-web
    container_name: quickgo_admin
    command: npm run dev
    volumes:
      - ./admin-web:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - quickgo_network

  redis:
    image: redis:7-alpine
    container_name: quickgo_redis
    ports:
      - "6379:6379"
    networks:
      - quickgo_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  celery:
    build: ./backend
    container_name: quickgo_celery
    command: celery -A config worker -l info
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=`${DEBUG}
      - SECRET_KEY=`${SECRET_KEY}
      - DB_NAME=`${DB_NAME}
      - DB_USER=`${DB_USER}
      - DB_PASSWORD=`${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=`${REDIS_URL}
    depends_on:
      - db
      - redis
    networks:
      - quickgo_network

  celery-beat:
    build: ./backend
    container_name: quickgo_celery_beat
    command: celery -A config beat -l info
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=`${DEBUG}
      - SECRET_KEY=`${SECRET_KEY}
      - DB_NAME=`${DB_NAME}
      - DB_USER=`${DB_USER}
      - DB_PASSWORD=`${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=`${REDIS_URL}
    depends_on:
      - db
      - redis
    networks:
      - quickgo_network

volumes:
  postgres_data:
  static_volume:
  media_volume:

networks:
  quickgo_network:
    driver: bridge
"@

Create-FileWithContent -Path "docker-compose.yml" -Content $dockerComposeContent

# ============================================
# 2. BACKEND - ESTRUCTURA
# ============================================
Write-Host "[2/7] Creando estructura Backend..." -ForegroundColor Cyan

# Crear directorios backend
$backendDirs = @(
    "backend/config/settings",
    "backend/apps/users",
    "backend/apps/restaurants",
    "backend/apps/products",
    "backend/apps/orders",
    "backend/apps/payments",
    "backend/apps/deliveries",
    "backend/apps/notifications",
    "backend/apps/analytics",
    "backend/media/restaurants",
    "backend/media/products",
    "backend/media/users",
    "backend/static",
    "backend/templates"
)

foreach ($dir in $backendDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$dockerfileContent = @"
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Permisos para entrypoint
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"@

Create-FileWithContent -Path "backend/Dockerfile" -Content $dockerfileContent

$requirementsContent = @"
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.0
django-filter==23.3
drf-yasg==1.21.7

# Database
psycopg2-binary==2.9.9

# Environment
python-decouple==3.8

# Images
Pillow==10.1.0

# Celery & Redis
celery==5.3.4
redis==5.0.1

# Server
gunicorn==21.2.0
whitenoise==6.6.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
"@

Create-FileWithContent -Path "backend/requirements.txt" -Content $requirementsContent

$entrypointContent = @"
#!/bin/bash

echo "Esperando a PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL iniciado"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando servidor..."
exec "`$@"
"@

Create-FileWithContent -Path "backend/entrypoint.sh" -Content $entrypointContent

$dockerignoreContent = @"
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
*.sqlite3
db.sqlite3
.env
.git
.gitignore
*.log
media/
static_root/
"@

Create-FileWithContent -Path "backend/.dockerignore" -Content $dockerignoreContent

$managePyContent = @"
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
"@

Create-FileWithContent -Path "backend/manage.py" -Content $managePyContent

# ============================================
# 3. BACKEND - CONFIG
# ============================================
Write-Host "[3/7] Configurando Django..." -ForegroundColor Cyan

$configInitContent = @"
from .celery import app as celery_app

__all__ = ('celery_app',)
"@

Create-FileWithContent -Path "backend/config/__init__.py" -Content $configInitContent

$celeryContent = @"
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('quick_go')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-pending-orders': {
        'task': 'apps.orders.tasks.check_pending_orders',
        'schedule': crontab(minute='*/5'),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
"@

Create-FileWithContent -Path "backend/config/celery.py" -Content $celeryContent

$urlsContent = @"
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Quick Go API",
        default_version='v1',
        description="API para sistema de delivery Quick Go",
        contact=openapi.Contact(email="contact@quickgo.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API URLs
    path('api/auth/', include('apps.users.urls')),
    path('api/restaurants/', include('apps.restaurants.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/deliveries/', include('apps.deliveries.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Quick Go Admin"
admin.site.site_title = "Quick Go Admin Portal"
admin.site.index_title = "Bienvenido al Panel de Administración"
"@

Create-FileWithContent -Path "backend/config/urls.py" -Content $urlsContent

$wsgiContent = @"
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
"@

Create-FileWithContent -Path "backend/config/wsgi.py" -Content $wsgiContent

$asgiContent = @"
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_asgi_application()
"@

Create-FileWithContent -Path "backend/config/asgi.py" -Content $asgiContent

# Settings files
Create-FileWithContent -Path "backend/config/settings/__init__.py" -Content ""

$baseSettingsContent = @"
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    
    # Local apps
    'apps.users',
    'apps.restaurants',
    'apps.products',
    'apps.orders',
    'apps.payments',
    'apps.deliveries',
    'apps.notifications',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_LIFETIME', default=1, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
"@

Create-FileWithContent -Path "backend/config/settings/base.py" -Content $baseSettingsContent

$devSettingsContent = @"
from .base import *

DEBUG = True

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
"@

Create-FileWithContent -Path "backend/config/settings/development.py" -Content $devSettingsContent

$prodSettingsContent = @"
from .base import *

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
"@

Create-FileWithContent -Path "backend/config/settings/production.py" -Content $prodSettingsContent

# ============================================
# 4. BACKEND - APPS
# ============================================
Write-Host "[4/7] Creando apps Django..." -ForegroundColor Cyan

$apps = @("users", "restaurants", "products", "orders", "payments", "deliveries", "notifications", "analytics")

foreach ($app in $apps) {
    $appCapitalized = $app.Substring(0,1).ToUpper() + $app.Substring(1)
    
    # __init__.py
    Create-FileWithContent -Path "backend/apps/$app/__init__.py" -Content "default_app_config = 'apps.$app.apps.${appCapitalized}Config'"
    
    # apps.py
    $appsContent = @"
from django.apps import AppConfig


class ${appCapitalized}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.$app'
    verbose_name = '$appCapitalized'
"@
    Create-FileWithContent -Path "backend/apps/$app/apps.py" -Content $appsContent
    
    # models.py
    Create-FileWithContent -Path "backend/apps/$app/models.py" -Content "from django.db import models`n`n# Create your models here."
    
    # views.py
    Create-FileWithContent -Path "backend/apps/$app/views.py" -Content "from rest_framework import viewsets`n`n# Create your views here."
    
    # serializers.py
    Create-FileWithContent -Path "backend/apps/$app/serializers.py" -Content "from rest_framework import serializers`n`n# Create your serializers here."
    
    # urls.py
    $urlsAppContent = @"
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
"@
    Create-FileWithContent -Path "backend/apps/$app/urls.py" -Content $urlsAppContent
    
    # admin.py
    Create-FileWithContent -Path "backend/apps/$app/admin.py" -Content "from django.contrib import admin`n`n# Register your models here."
    
    # tests.py
    Create-FileWithContent -Path "backend/apps/$app/tests.py" -Content "from django.test import TestCase`n`n# Create your tests here."
}

# Modelo de usuarios personalizado
$usersModelsContent = @"
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CUSTOMER = 'CUSTOMER', 'Cliente'
        DRIVER = 'DRIVER', 'Repartidor'
        RESTAURANT = 'RESTAURANT', 'Restaurante'
    
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_user_type_display()})'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Driver(models.Model):
    class VehicleType(models.TextChoices):
        BIKE = 'BIKE', 'Bicicleta'
        MOTORCYCLE = 'MOTORCYCLE', 'Motocicleta'
        CAR = 'CAR', 'Automóvil'
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices)
    vehicle_plate = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    
    class Meta:
        verbose_name = 'Repartidor'
        verbose_name_plural = 'Repartidores'
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.vehicle_plate}'
"@

Create-FileWithContent -Path "backend/apps/users/models.py" -Content $usersModelsContent

# ============================================
# 5. ADMIN-WEB
# ============================================
Write-Host "[5/7] Creando panel web de administración..." -ForegroundColor Cyan

$adminDirs = @(
    "admin-web/public/images",
    "admin-web/public/icons",
    "admin-web/src/app/(auth)/login",
    "admin-web/src/app/dashboard",
    "admin-web/src/app/api/auth",
    "admin-web/src/components/ui",
    "admin-web/src/components/dashboard",
    "admin-web/src/lib",
    "admin-web/src/styles"
)

foreach ($dir in $adminDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$adminDockerfileContent = @"
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"@

Create-FileWithContent -Path "admin-web/Dockerfile" -Content $adminDockerfileContent

$adminPackageContent = @"
{
  "name": "quickgo-admin",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.2",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5",
    "eslint": "^8",
    "eslint-config-next": "14.0.4"
  }
}
"@

Create-FileWithContent -Path "admin-web/package.json" -Content $adminPackageContent

$nextConfigContent = @"
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
}

module.exports = nextConfig
"@

Create-FileWithContent -Path "admin-web/next.config.js" -Content $nextConfigContent

$tsconfigContent = @"
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"@

Create-FileWithContent -Path "admin-web/tsconfig.json" -Content $tsconfigContent

$tailwindConfigContent = @"
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"@

Create-FileWithContent -Path "admin-web/tailwind.config.js" -Content $tailwindConfigContent

$appLayoutContent = @"
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Quick Go Admin',
  description: 'Panel de administración Quick Go',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
"@

Create-FileWithContent -Path "admin-web/src/app/layout.tsx" -Content $appLayoutContent

$appPageContent = @"
export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-4">Quick Go Admin</h1>
      <p className="text-xl">Panel de Administración</p>
    </main>
  )
}
"@

Create-FileWithContent -Path "admin-web/src/app/page.tsx" -Content $appPageContent

$globalsContent = @"
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: rgb(var(--background-rgb));
}
"@

Create-FileWithContent -Path "admin-web/src/styles/globals.css" -Content $globalsContent

# ============================================
# 6. MOBILE-CUSTOMER
# ============================================
Write-Host "[6/7] Creando app móvil para clientes..." -ForegroundColor Cyan

$customerDirs = @(
    "mobile-customer/src/api",
    "mobile-customer/src/navigation",
    "mobile-customer/src/screens/Auth",
    "mobile-customer/src/screens/Home",
    "mobile-customer/src/screens/Restaurant",
    "mobile-customer/src/screens/Cart",
    "mobile-customer/src/screens/Orders",
    "mobile-customer/src/screens/Profile",
    "mobile-customer/src/components/common",
    "mobile-customer/src/components/Restaurant",
    "mobile-customer/src/components/Product",
    "mobile-customer/src/components/Order",
    "mobile-customer/src/store/slices",
    "mobile-customer/src/utils",
    "mobile-customer/src/types",
    "mobile-customer/src/theme",
    "mobile-customer/assets/images",
    "mobile-customer/assets/icons"
)

foreach ($dir in $customerDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$customerPackageContent = @"
{
  "name": "quickgo-customer",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~49.0.15",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@react-navigation/bottom-tabs": "^6.5.11",
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4",
    "axios": "^1.6.2",
    "react-native-maps": "^1.8.3",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "react-native-vector-icons": "^10.0.3"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.14",
    "typescript": "^5.1.3"
  }
}
"@

Create-FileWithContent -Path "mobile-customer/package.json" -Content $customerPackageContent

$appJsonContent = @"
{
  "expo": {
    "name": "QuickGo",
    "slug": "quickgo-customer",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.quickgo.customer"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.quickgo.customer"
    }
  }
}
"@

Create-FileWithContent -Path "mobile-customer/app.json" -Content $appJsonContent

$customerAppContent = @"
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import { store } from './src/store';

export default function App() {
  return (
    <Provider store={store}>
      <NavigationContainer>
        {/* Navigation will go here */}
      </NavigationContainer>
    </Provider>
  );
}
"@

Create-FileWithContent -Path "mobile-customer/App.tsx" -Content $customerAppContent

$storeIndexContent = @"
import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    // reducers will go here
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
"@

Create-FileWithContent -Path "mobile-customer/src/store/index.ts" -Content $storeIndexContent

# ============================================
# 7. MOBILE-DRIVER
# ============================================
Write-Host "[7/7] Creando app móvil para repartidores..." -ForegroundColor Cyan

$driverDirs = @(
    "mobile-driver/src/api",
    "mobile-driver/src/navigation",
    "mobile-driver/src/screens/Auth",
    "mobile-driver/src/screens/Home",
    "mobile-driver/src/screens/Deliveries",
    "mobile-driver/src/screens/Earnings",
    "mobile-driver/src/screens/Profile",
    "mobile-driver/src/components/common",
    "mobile-driver/src/components/Delivery",
    "mobile-driver/src/components/Earnings",
    "mobile-driver/src/store/slices",
    "mobile-driver/src/services",
    "mobile-driver/src/utils",
    "mobile-driver/src/types",
    "mobile-driver/src/theme",
    "mobile-driver/assets/images",
    "mobile-driver/assets/icons"
)

foreach ($dir in $driverDirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

$driverPackageContent = @"
{
  "name": "quickgo-driver",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~49.0.15",
    "react": "18.2.0",
    "react-native": "0.72.6",
    "@react-navigation/native": "^6.1.9",
    "@react-navigation/stack": "^6.3.20",
    "@reduxjs/toolkit": "^2.0.1",
    "react-redux": "^9.0.4",
    "axios": "^1.6.2",
    "react-native-maps": "^1.8.3",
    "expo-location": "~16.3.0",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "react-native-vector-icons": "^10.0.3"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.14",
    "typescript": "^5.1.3"
  }
}
"@

Create-FileWithContent -Path "mobile-driver/package.json" -Content $driverPackageContent

$driverAppJsonContent = @"
{
  "expo": {
    "name": "QuickGo Driver",
    "slug": "quickgo-driver",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": false,
      "bundleIdentifier": "com.quickgo.driver"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": "com.quickgo.driver",
      "permissions": [
        "ACCESS_COARSE_LOCATION",
        "ACCESS_FINE_LOCATION",
        "FOREGROUND_SERVICE"
      ]
    }
  }
}
"@

Create-FileWithContent -Path "mobile-driver/app.json" -Content $driverAppJsonContent

$driverAppContent = @"
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider } from 'react-redux';
import { store } from './src/store';

export default function App() {
  return (
    <Provider store={store}>
      <NavigationContainer>
        {/* Navigation will go here */}
      </NavigationContainer>
    </Provider>
  );
}
"@

Create-FileWithContent -Path "mobile-driver/App.tsx" -Content $driverAppContent

$driverStoreContent = @"
import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    // reducers will go here
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
"@

Create-FileWithContent -Path "mobile-driver/src/store/index.ts" -Content $driverStoreContent

# ============================================
# FINALIZAR
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  PROYECTO QUICK GO CREADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Estructura creada en: " -NoNewline -ForegroundColor White
Write-Host "$((Get-Location).Path)" -ForegroundColor Yellow
Write-Host ""

Write-Host "PROXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Configurar variables de entorno:" -ForegroundColor White
Write-Host "   Copy-Item .env.example .env" -ForegroundColor Yellow
Write-Host "   code .env" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Levantar servicios Docker:" -ForegroundColor White
Write-Host "   docker-compose up --build" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. En otra terminal PowerShell:" -ForegroundColor White
Write-Host "   docker-compose exec backend python manage.py createsuperuser" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Para las apps moviles:" -ForegroundColor White
Write-Host "   cd mobile-customer" -ForegroundColor Yellow
Write-Host "   npm install" -ForegroundColor Yellow
Write-Host "   npm run android" -ForegroundColor Yellow
Write-Host ""
Write-Host "Lee el README.md para mas informacion" -ForegroundColor Magenta
Write-Host ""

Write-Host "Listo para usar!" -ForegroundColor Green