from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.conf.enable_utc = False
app.conf.update(timezone='Asia/Dhaka')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
}

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {

}
