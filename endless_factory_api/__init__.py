# from .celery import app 
from . import disable_csrf
from .celery import app as celery_app

__all__ = ('celery_app',)