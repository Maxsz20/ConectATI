FROM python:3.11-slim

# Instalación de Apache y dependencias
RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    && a2enmod headers \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear carpetas necesarias
WORKDIR /app
RUN mkdir -p /app/web/static /app/web/db /app/web/media

# Copiar requirements.txt y dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar todo el proyecto al contenedor
COPY . /app

# Configurar Apache con archivo WSGI personalizado
COPY web/django.conf /etc/apache2/sites-available/django.conf
RUN a2ensite django.conf && a2dissite 000-default.conf

# Collect static sin crashear si falla
RUN mkdir -p /app/web/static && \
    python3 /app/web/manage.py collectstatic --noinput || true

# Exponer puerto (Apache corre en 80)
EXPOSE 80

# Comando para ejecutar Apache
CMD ["apachectl", "-D", "FOREGROUND"]
