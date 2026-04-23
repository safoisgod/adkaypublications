"""
Celery configuration for A-D Kay Publications.
"""
import os
from celery import Celery

os.environ['DJANGO_SETTINGS_MODULE'] = os.getenv(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.production'
)

app = Celery('adkaypublications')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
