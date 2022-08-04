from dateutil.relativedelta import relativedelta
import datetime
delta = relativedelta(months=6)
six_month_away = datetime.date.today() - delta
print(abs((six_month_away - datetime.date.today()).days))