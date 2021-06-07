# Celery entrance
from celery import Celery

# Create Celery instance
celery_app = Celery('meiduo')

# Load configuration
celery_app.config_from_object('celery_tasks.config')

# Register tasks
celery_app.autodiscover_tasks(['celery_tasks.sms'])