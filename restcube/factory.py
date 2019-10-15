# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_cors import CORS

from flask_redis import FlaskRedis
from celery import Celery
from furl import furl


def create_app():
    app = Flask('restcube')
    CORS(app)
    # configuration
    app.config['COGNITO_REGION']=os.getenv('COGNITO_REGION', None)
    app.config['COGNITO_USERPOOL_ID']=os.getenv('COGNITO_USERPOOL_ID', None)
    # optional
    #'COGNITO_APP_CLIENT_ID': os.getenv('COGNITO_APP_CLIENT_ID', None),  # client ID you wish to verify user is authenticated against
        
    #'COGNITO_CHECK_TOKEN_EXPIRATION': False,  # disable token expiration checking for testing purposes
    #'COGNITO_JWT_HEADER_NAME': os.getenv('COGNITO_JWT_HEADER_NAME', None),
    #'COGNITO_JWT_HEADER_PREFIX': 'Bearer',
    return app

def make_celery(app=None):
    app = app or create_app()

    redis_password = os.getenv("REDIS_PASSWORD", None)
    broker_url = furl(os.getenv("CELERY_BROKER", "redis://localhost:6379"))
    result_backend_url = furl(os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"))

    if redis_password is not None:
        broker_url.username = ""
        broker_url.password = redis_password
        result_backend_url.username = ""
        result_backend_url.password = redis_password

    print(broker_url.tostr())
    app.config.update(
        CELERY_BROKER_URL=broker_url.tostr(),
        CELERY_RESULT_BACKEND=result_backend_url.tostr())

    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

