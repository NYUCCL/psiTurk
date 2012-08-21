#!/bin/bash

exec gunicorn -c config_gunicorn.py 'app:app'
