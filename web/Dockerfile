FROM python:3.11-slim

# Instalación de Apache y dependencias
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de la app
WORKDIR /app

# Instalación de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del proyecto
COPY . /app

# Configuración de Apache
COPY django.conf /etc/apache2/sites-available/django.conf
RUN a2ensite django.conf && a2dissite 000-default.conf

# Asegura que la ruta STATIC_ROOT exista antes del collectstatic
RUN mkdir -p /app/static

# Ejecuta collectstatic en la ruta correcta
RUN python manage.py collectstatic --noinput \
    && chmod -R 755 /app/app/static

# Exponer puerto
EXPOSE 80

# Ejecutar Apache
CMD ["apachectl", "-D", "FOREGROUND"]
