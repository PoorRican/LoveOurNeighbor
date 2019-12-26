#!/bin/bash

BIND=0.0.0.0:8000
WORKERS=2
LOG_DIR=/var/log/gunicorn
gunicorn frontend.wsgi:application \
    --bind=$BIND \
    --log-level "debug" \
    #--access-logfile=$LOG_DIR/alog.log \
    #--error-logfile=$LOG_DIR/elog.log
