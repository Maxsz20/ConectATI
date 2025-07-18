FROM python:3.11-slim

# Instalacion de Apache y componentes necesarios
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crea el directorio de la aplicación
WORKDIR /app

# Copia dependencias e instala del requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
COPY django.conf /etc/apache2/sites-available/django.conf
RUN a2ensite django.conf && a2dissite 000-default.conf

RUN python manage.py collectstatic --noinput

# Exponer el puerto 80
EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]

