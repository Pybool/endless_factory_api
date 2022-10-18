import itertools
from django.db import models
from accounts.models import User
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
    
ATTACHMENT_TYPE_OPTIONS = (
  ('pdf', 'pdf'),
  ('docx', 'docx'),
)

class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=10,default='')
    phone = models.CharField(max_length=20,default='')
    resume = models.ImageField(upload_to="",blank=True)
    gender = models.CharField(max_length=10,default='')
    type = models.CharField(max_length=15,default='')
 
    # def __str__(self):
    #     return self.email
 
class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='')
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to="")
    location = models.CharField(max_length=250)
    company_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100)
 
    # def __str__ (self):
    #     return self.company_name
 
class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=200)
    role = models.CharField(max_length=250,default='')
    currency = models.CharField(max_length=10,null=True)
    salary = models.FloatField()
    image = models.ImageField(upload_to="")
    description = models.TextField(max_length=1500)
    slug = models.SlugField(null=True, unique=True, editable=False)
    experience = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    skills = models.CharField(max_length=1000)
    creation_date = models.DateField(auto_now=True)
    
    def generate_slug(self):
        value = self.title
        slug_candidate = slug_original = slugify(value, allow_unicode=True)
        for i in itertools.count(1):
            if not Job.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)

        self.slug = slug_candidate
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_slug()
        super().save(*args, **kwargs)
    # def __str__ (self):
    #     return self.title
 
class Applications(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    apply_date = models.DateField(auto_now=True)
    
    def resume(self):
        resume = []
        lookups =  Q(attachment_type='pdf') | Q(attachment_type='docx')
        for attachment in self.applicantsresume_set.filter(lookups): 
            if attachment.file and hasattr(attachment.file, 'url'):
                resume.append(attachment.file.url)
        return resume[0]
 
    # def __str__ (self):
    #     return str(self.applicant)
    
class ApplicantsResume(models.Model):
    application = models.ForeignKey(Applications, default=None, on_delete=models.CASCADE)
    attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='pdf')
    file = models.FileField(upload_to='careers_jobs_resume/%Y/%m/%d/', null=True, blank=False)

    def url(self):
        return self.file.url if self.file and hasattr(self.file, 'url') else None
