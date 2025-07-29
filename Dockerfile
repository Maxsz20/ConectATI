    FROM python:3.11-slim

    # Instalación de Apache y dependencias
    RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    && a2enmod headers \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

    # Carpeta de la app
    WORKDIR /web

    # Instalación de dependencias
    COPY web/requirements.txt ./requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copia del proyecto
    COPY . /web

    # Configuración de Apache
    COPY web/django.conf /etc/apache2/sites-available/django.conf
    RUN a2ensite django.conf && a2dissite 000-default.conf

    # Asegura que la ruta STATIC_ROOT exista antes del collectstatic
    RUN mkdir -p /web/static

    # Ejecuta collectstatic en la ruta correcta
    RUN python manage.py collectstatic --noinput \
        && chmod -R 755 /web/app/static

    # Exponer puerto
    EXPOSE 80

    # Ejecutar Apache
    CMD ["apachectl", "-D", "FOREGROUND"]