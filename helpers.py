import pytz
import datetime
from django.utils import timezone
from django.utils.timezone import localtime, now
from dateutil.relativedelta import relativedelta

class Datetimeutils(object):
    
    def __init__(self,duration):
        self.duration = duration

    def months_previous_days_from_now(self,months):
        delta = relativedelta(months=months)
        time_month_previous = datetime.date.today() - delta
        return abs((datetime.date.today()-time_month_previous).days) * 24

    def convert_period_to_hours(self,period):
        
        hrs_year = 8760
        hrs_leap_year = 8784
        lst = {'28':672,'29':696,'30':720,'31':744}
        month = [31,28]

    def get_pages_created_on_date(self,filter):

        if filter == 'day': hours = 24 * self.duration
        if filter == 'week': hours = 168 * self.duration
        if filter == 'month': hours = self.months_previous_days_from_now(self.duration) 
        if filter == 'year': hours = self.months_previous_days_from_now(12) 
        now = timezone.now()
        end_date = now.replace(minute=0, second=0, microsecond=0)
        start_date = end_date - datetime.timedelta(hours=hours)
        return (start_date , end_date)

x = Datetimeutils(1)
val = x.months_previous_days_from_now(2)
print(val)
