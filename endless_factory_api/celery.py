from datetime import timedelta
import os
from celery import Celery
#set the default django settings to celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endless_factory_api.settings')
app = Celery('endless_factory_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))