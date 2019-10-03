#!/bin/bash

# datacube system init
datacube system init

# start server
gunicorn -b "0.0.0.0:8000" "restcube.app:app"
