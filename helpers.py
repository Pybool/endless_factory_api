import pytz
import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def get_user_timezone(tz):
    from datetime import datetime

    user_tz = pytz.timezone(tz) 
    time_in_user_tz = datetime.now(user_tz)
    return time_in_user_tz#.strftime("%Y-%m-%d %H:%M:%S")

def convert_to_timezone(input_dt, current_tz='', target_tz=''):
    current_tz = pytz.timezone(current_tz)
    target_tz = pytz.timezone(target_tz)
    target_dt = current_tz.localize(input_dt).astimezone(target_tz)
    return target_tz.normalize(target_dt) 
# def convert_to_timezone(dt,tz):
#     return dt(tz)

def get_timezone_datetime():
    import datetime
    current_date = datetime.datetime.now()

    current_date = current_date.\
        replace(tzinfo=datetime.timezone.utc)

    return current_date.isoformat()
  

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
        end_date = now#.replace(minute=0, second=0, microsecond=0)
        start_date = end_date - datetime.timedelta(hours=hours)
        return (start_date , end_date)

class DocxEditor(object):
    
    def __init__(self,sender,recepient):
        self.sender = sender
        self.recepient = recepient
    
    def convert_docx_to_pdf(self,filename):
        try:
            newpdf = f"{filename.replace('.docx','')+'@endlessfactory_generated'+str(timezone.now())}.pdf".strip()
            doc = Document(filename)
            fullText = []
            for para in doc.paragraphs:
                fullText.append(para.text.replace("(Seller)",self.recepient).replace("(Buyer)",self.sender))
            self.generate_pdf(fullText,newpdf)
            return newpdf
        
        except:
            pass


    def generate_pdf(self,document_text,newpdf):
        try:
            doc = SimpleDocTemplate(
                    newpdf,
                    pagesize=letter,
                    rightMargin=72, leftMargin=72,
                    topMargin=72, bottomMargin=18,
                    )
            styles = getSampleStyleSheet()
            flowables = []
            spacer = Spacer(1, 0.25*inch)
            for i in range(len(document_text)):
                text = document_text[i]
                para = Paragraph(text, style=styles["Normal"])
                flowables.append(para)
                flowables.append(spacer)
            doc.build(flowables)
        except:
            pass
