# Quick Go - AplicaciÃ³n de Delivery

Sistema completo de delivery con panel de administraciÃ³n web y aplicaciones mÃ³viles.

## ðŸš€ TecnologÃ­as

- **Backend**: Django + Django REST Framework
- **Base de Datos**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Panel Admin**: Next.js + TypeScript
- **Apps MÃ³viles**: React Native + TypeScript
- **ContainerizaciÃ³n**: Docker + Docker Compose

## ðŸ“ Estructura del Proyecto

```
quickgo/
â”œâ”€â”€ backend/           # API Django REST Framework
â”œâ”€â”€ admin-web/         # Panel administrativo (Next.js)
â”œâ”€â”€ mobile-customer/   # App mÃ³vil para clientes
â””â”€â”€ mobile-driver/     # App mÃ³vil para repartidores
```

## ðŸ› ï¸ InstalaciÃ³n y ConfiguraciÃ³n

### Requisitos Previos

- Docker Desktop para Windows
- Node.js 18+ y npm
- Visual Studio Code
- Android Studio (opcional, para desarrollo mÃ³vil)

### 1. ConfiguraciÃ³n Inicial

```powershell
# Copiar archivo de variables de entorno
Copy-Item .env.example .env

# Editar .env con tus configuraciones
code .env
```

### 2. Levantar Backend con Docker

```powershell
# Construir y levantar contenedores
docker-compose up --build

# En otra terminal PowerShell, ejecutar migraciones
docker-compose exec backend python manage.py migrate

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```

### 3. Panel de AdministraciÃ³n Web

```powershell
cd admin-web
npm install
npm run dev
```

Acceder a: http://localhost:3000

### 4. App MÃ³vil - Clientes

```powershell
cd mobile-customer
npm install
npm run android
```

### 5. App MÃ³vil - Repartidores

```powershell
cd mobile-driver
npm install
npm run android
```

## ðŸ“± Accesos

- **API Backend**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **Panel Web Admin**: http://localhost:3000
- **API Documentation**: http://localhost:8000/swagger

## ðŸ‘¥ Tipos de Usuarios

1. **Administrador**: GestiÃ³n completa del sistema (web)
2. **Cliente**: Realizar y rastrear pedidos (mÃ³vil)
3. **Repartidor**: Aceptar y entregar pedidos (mÃ³vil)

## ðŸ”§ Comandos Ãštiles (PowerShell)

```powershell
# Ver logs del backend
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Detener todos los servicios
docker-compose down

# Limpiar volÃºmenes (cuidado: borra la BD)
docker-compose down -v
```

## ðŸ“ Desarrollo

### Backend (Django)

```powershell
# Crear nueva app
docker-compose exec backend python manage.py startapp nombre_app

# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Aplicar migraciones
docker-compose exec backend python manage.py migrate

# Shell de Django
docker-compose exec backend python manage.py shell
```

## ðŸ‘¨â€ðŸ’» Autor

Desarrollado por Cristian - UPEC
Universidad PolitÃ©cnica Estatal del Carchi
