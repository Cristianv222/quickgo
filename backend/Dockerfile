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
# Usar CMD directamente para evitar problemas con entrypoint
CMD bash -c "echo 'Esperando a PostgreSQL...' && \
    while ! nc -z db 5432; do sleep 0.1; done && \
    echo 'PostgreSQL iniciado' && \
    echo 'Aplicando migraciones...' && \
    python manage.py migrate --noinput && \
    echo 'Recolectando archivos estáticos...' && \
    python manage.py collectstatic --noinput && \
    echo 'Iniciando servidor...' && \
    python manage.py runserver 0.0.0.0:8000"