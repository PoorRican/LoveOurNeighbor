FROM python:3.7

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /LON
WORKDIR /LON

# packages for postgresql
RUN apt-get update && apt-get install postgresql libpq-dev postgresql-contrib -y
# packages for python-pillow
#RUN apt-get install build-base python-dev py-pip jpeg-dev zlib-dev


COPY requirements.txt /LON/
RUN pip install -r requirements.txt

COPY . /LON/

RUN chmod +x /LON/configs/django/entrypoint.sh

#=========================#
# DATABASE INITIALIZATION #
#=========================#
RUN bash utils/clear_migrations.sh

RUN python manage.py makemigrations public people tag campaign ministry donation news
RUN python manage.py migrate --noinput
# delay migration to avoid `django.db.InconsistentMigrationHistory` being thrown
RUN python manage.py makemigrations explore comment
RUN python manage.py migrate --noinput

RUN python populate.py
