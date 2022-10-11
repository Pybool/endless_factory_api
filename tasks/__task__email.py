from accounts.mailservice import Mailservice
from celery import shared_task 
# from celery.decorators import task
from django.core.mail import send_mail
from time import sleep
from django.db import transaction
# from .models import Promotion

from datetime import datetime
from decimal import Decimal
from math import ceil


@shared_task
def sleepy(duration):
    sleep(duration)
    return None

@shared_task
def send_password_reset_email_task(mail_parameters):
    Mailservice.pass_reset_send_mail(mail_parameters)
    return None

@shared_task
def send_email_task(mail_parameters):
    print(mail_parameters)
    Mailservice.user_send_mail(mail_parameters)
    return None

@shared_task
def send_order_status_mail_task(mail_parameters):
    print(mail_parameters)
    Mailservice.order_send_mail(mail_parameters)
    return None

