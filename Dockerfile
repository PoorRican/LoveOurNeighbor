# retrieved from: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/
###########
# BUILDER #
###########

# pull official base image
FROM python:3.8.0-alpine as builder

# set work directory
WORKDIR /usr/src/LON

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev

# lint
# RUN pip install --upgrade pip
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
FROM python:3.8.0-alpine

# create home directory for the app user
ENV HOME=/home/django
RUN mkdir -p $HOME

# create the app user
RUN addgroup -S django && adduser -S django -G django

# create the appropriate directories
ENV APP_HOME=$HOME/lon
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
COPY --from=builder /usr/src/LON/wheels /wheels
COPY --from=builder /usr/src/LON/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R django:django $APP_HOME
RUN chmod +x $APP_HOME/configs/django/entrypoint.sh

# change to the app user
USER django

# run entrypoint.prod.sh
ENTRYPOINT ["/home/django/lon/configs/django/entrypoint.sh"]