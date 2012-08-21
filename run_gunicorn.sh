#!/bin/bash

LOCALHOST=0.0.0.0
PORT=8000
THREADS=4

LOGFILE=server.log
LOGLEVEL=warning

exec gunicorn -w $THREADS --log-file $LOGFILE --log-level $LOGLEVEL -b "$LOCALHOST:$PORT" app:app
