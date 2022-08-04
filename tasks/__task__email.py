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

# @shared_task()
# def promotion_prices(reduction_amount, obj_id):
#     with transaction.atomic():
#         promotions = Promotion.products_on_promotion.through.objects.filter(promotion_id=obj_id)
#         reduction = reduction_amount / 100

#         for promo in promotions:
#             if promo.price_override == False:
#                 store_price = promo.product_inventory_id.store_price
#                 new_price = ceil(store_price - (store_price * Decimal(reduction)))
#                 promo.promo_price = Decimal(new_price)
#                 promo.save()


# @shared_task()
# def promotion_management():
#     with transaction.atomic():
#         promotions = Promotion.objects.filter(is_schedule=True)

#         now = datetime.now().date()

#         for promo in promotions:
#             if promo.is_schedule:
#                 if promo.promo_end < now:
#                     promo.is_active = False
#                     promo.is_schedule = False
#                 else:
#                     if promo.promo_start <= now:
#                         promo.is_active = True
#                     else:
#                         promo.is_active = False
#             promo.save()