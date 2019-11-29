#!/bin/sh

# startup script for production environment

# wait until database container is online
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# ensure db has been configured
python manage.py makemigrations public people tag campaign ministry donation news
python manage.py migrate --noinput
# delay migration to avoid `django.db.InconsistentMigrationHistory` being thrown
python manage.py makemigrations explore comment
python manage.py migrate --noinput

python populate.py

# collect staticfiles (maybe they should be manually uploaded to CDN)
python manage.py collectstatic --no-input --clear

python manage.py assets build

exec "$@"
