# retrieved from: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
###########
# BUILDER #
###########

# pull official base image
FROM python as builder

# set work directory
WORKDIR /usr/src/LON

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# lint
RUN pip install --upgrade pip
# RUN pip install flake8
# COPY . /usr/src/LON/
# RUN flake8 --ignore=E501,F401 .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/LON/wheels -r requirements.txt

#########
# FINAL #
#########

# pull official base image
FROM python

# create home directory for the app user
ENV HOME=/home/django
RUN mkdir -p $HOME

# create the app user
RUN addgroup --system django && adduser --system django --home $HOME && adduser django django

# create the appropriate directories
ENV APP_HOME=$HOME/lon
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
RUN mkdir /var/log/gunicorn
WORKDIR $APP_HOME

# install dependencies
COPY --from=builder /usr/src/LON/wheels /wheels
COPY --from=builder /usr/src/LON/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME
COPY ./static/media/img $APP_HOME/mediafiles/img

# Clear Environment
#RUN sh utils/clear_migrations.sh
#RUN python manage.py makemigrations public people tag campaign ministry donation post
#RUN python manage.py migrate --noinput
# delay migration to avoid `django.db.InconsistentMigrationHistory` being thrown
#RUN python manage.py makemigrations explore comment
RUN python manage.py migrate --noinput

#RUN python populate.py

RUN chmod +x local_env.sh

# collect staticfiles (maybe they should be manually uploaded to CDN)
# RUN python manage.py collectstatic --no-input --clear

#RUN python manage.py assets build

# chown all the files to the app user
RUN chown -R django:django $APP_HOME
RUN chown -R django:django $APP_HOME/mediafiles
RUN chown -R django:django /var/log/gunicorn

RUN chmod +x $APP_HOME/configs/django/entrypoint.sh
RUN chmod +x $APP_HOME/configs/django/gunicorn_start.sh

# change to the app user
USER django

# run entrypoint.prod.sh
#ENTRYPOINT ["/home/django/lon/configs/django/entrypoint.sh"]