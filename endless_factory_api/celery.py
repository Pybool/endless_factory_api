from datetime import timedelta
import os
from celery import Celery
#set the default django settings to celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endless_factory_api.settings')
app = Celery('endless_factory_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app.conf.broker_url = BASE_REDIS_URL
#creating a celery beat scheduler to start the tasks
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

app.conf.beat_schedule = {
    'check-campaigns': {
        'task': '__task__promotions.checkCampaignsManagement',
        'schedule': timedelta(seconds=10)
    }
}

app.conf.timezone = 'UTC'
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
    
