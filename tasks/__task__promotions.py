from celery import shared_task 
# from celery.decorators import task
from time import sleep
from django.db import transaction

from marketing.models import Campaign as Promotion
from datetime import datetime
from decimal import Decimal
from math import ceil

@shared_task()
def promotion_management():
    with transaction.atomic():
        promotions = Promotion.objects.filter(is_schedule=True)

        now = datetime.now().date()
        for promo in promotions:
            if promo.is_schedule:
                if promo.promo_end < now:
                    promo.is_active = False
                    promo.is_schedule = False
                    promo.discount = Decimal(0.00)
                else:
                    if promo.promo_start <= now:
                        promo.is_active = True
                    else:
                        promo.is_active = False
            promo.save()