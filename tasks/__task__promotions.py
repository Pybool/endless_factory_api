from celery import shared_task 
# from celery.decorators import task
from time import sleep
from django.db import transaction
from helpers import convert_to_timezone, get_timezone_datetime, get_user_timezone

from marketing.models import Campaign as Adverts
from datetime import datetime
from decimal import Decimal
from math import ceil
import logging
log = logging.getLogger(__name__)
import asyncio, time
import random, celery, json
from celery import Celery
from endless_factory_api.celery import app

class CampaignManager(celery.Task):
    def run(*args, **kwargs):
        def main():
            manage_campaigns()
            
        def is_sheduled(start,end,tz=''):
            print('Timezone ',tz)
            tznow = get_user_timezone(tz)
            print(f"Housekeeping {tznow , convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz)} and {tznow , convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)}")
            print(f"Housekeeping {tznow >= convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz)} and {tznow <= convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)}")
            return tznow >= convert_to_timezone(datetime.strptime(start, '%Y-%m-%d %H:%M:%S'),tz,tz) and tznow <= convert_to_timezone(datetime.strptime(end, '%Y-%m-%d %H:%M:%S'),tz,tz)
            
        def manage_campaigns():
            print("RUNNING CAMPAIGNS MANAGEMENT HOUSEKEEPING...")
            with transaction.atomic():
                adverts = Adverts.objects.filter()
                print(str(adverts))
                
                for advert in adverts:
                    print("In loop",advert.start_date,advert.end_date,advert.tz)
                    if not is_sheduled(advert.start_date,advert.end_date,advert.tz):
                        print("schedule??")
                        if advert.schedule_cmd == 'system':
                            advert.is_schedule = is_sheduled(advert.start_date,advert.end_date,advert.tz)
                    print("post schedule??")
                    if advert.is_schedule:
                        try:
                            tznow = get_user_timezone(advert.tz)
                            if convert_to_timezone(datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S'),advert.tz,advert.tz) < tznow:
                                advert.is_active = False
                                advert.is_schedule = False
                                advert.schedule_cmd = 'system'
                            else:
                                advert.is_schedule = True
                                advert.schedule_cmd = 'system'
                                
                            # print(f"{advert.is_schedule} Checking if advert should end {datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S')} {tznow}",datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S') < now)
                        except Exception as e:
                            print(str(e))
                            
                    elif not advert.is_schedule:
                        try:
                            tznow = get_user_timezone(advert.tz)
                            if convert_to_timezone(datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S'),advert.tz,advert.tz) > tznow:
                                advert.is_schedule = True
                                advert.schedule_cmd = 'system'
                            # print(f"{advert.is_schedule} Checking if advert should end {datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S')} {now}",datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S') < now)
                        except Exception as e:
                            print(str(e))
                    
                    try:
                        print("Fall throught" +str(advert.active_cmd))
                        if convert_to_timezone(datetime.strptime(advert.end_date, '%Y-%m-%d %H:%M:%S'),advert.tz,advert.tz) <= tznow:
                            if advert.active_cmd == 'system':
                                print("Supposed to turn off advert")
                                advert.is_active = False
                        # else:
                        #     advert.is_active = True
                    except Exception as e:
                        print(str(e))
                        
                    advert.save()
        main()
    
@app.task(name='__task__promotions.checkCampaignsManagement')
def checkCampaignsManagement():
    return CampaignManager.run()

