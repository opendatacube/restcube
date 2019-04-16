from flask import Flask
from celery import Celery
import os


def create_app():
    app = Flask('windsweeper')
    return app

def make_celery(app=None):
    app = app or create_app()

    app.config.update(
        CELERY_BROKER_URL=os.getenv("CELERY_BROKER", "redis://localhost:6379"),
        CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379"))

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