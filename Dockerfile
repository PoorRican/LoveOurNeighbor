FROM python:3

ENV PYTHONBUFFERED 1

RUN mkdir /LON
WORKDIR /LON

# packages for postgresql
RUN apt-get update && apt-get install postgresql -y
# packages for python-pillow
#RUN apt-get install build-base python-dev py-pip jpeg-dev zlib-dev


COPY requirements.txt /LON/
RUN pip install -r requirements.txt

COPY . /LON/

# setup db
#RUN python manage.py makemigrations public people tag campaign ministry donation comment explore news
#RUN python manage.py migrate --noinput
#RUN python populate.py
