from celery import Celery
import os


def make_celery(app=None):
    """
    Factory function to initialize and configure Celery instance with Flask app context.
    """
    broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    backend_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    if app:
        broker_url = app.config.get('CELERY_BROKER_URL', broker_url)
        backend_url = app.config.get('CELERY_RESULT_BACKEND', backend_url)

    celery = Celery(
        'smartdoc_tasks',
        broker=broker_url,
        backend=backend_url,
        include=['app.tasks.document_tasks']
    )

    if app:
        celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery()
