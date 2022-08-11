from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
import itertools
from django.urls import reverse


DELIVERY_OPTION_CHOICES = ( 
  ("Pickup Available", "Pickup Available"), 
  ("Delivery Available", "Delivery Available"), 
  ("Both", "Both")
)

PRICE_OPTION_CHOICES = ( 
  ("Fixed Price", "Fixed Price"), 
  ("Sliding Scale Depending On Volume", "Sliding Scale Depending On Volume"), 
  ("Contact Us", "Contact Us")
)

ATTACHMENT_TYPE_OPTIONS = (
  ('Image', 'Image'),
  ('Video', 'Video'),
)

# Create your models here
class Category(models.Model):
  name = models.CharField(max_length=50,unique=True)
  slug = models.SlugField(null=False, unique=True, editable=False)
  description = models.TextField(null=False, default='N/A')
  image = models.ImageField(upload_to='category_image', null=True, blank=False)
    
  def generate_slug(self):
    value = self.name
    slug_candidate = slug_original = slugify(value, allow_unicode=True)
    for i in itertools.count(1):
      if not Product.objects.filter(slug=slug_candidate).exists():
        break
      slug_candidate = '{}-{}'.format(slug_original, i)
    self.slug = slug_candidate
  
  def save(self, *args, **kwargs):
    if not self.pk:
      self.generate_slug()
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name

class Tag(models.Model):
  name = models.CharField(max_length=50,unique=True, null=False, error_messages={'required':'Name can not be blank'})
  slug = models.SlugField(null=False,unique=True, editable=False)
 
  def generate_slug(self):
    value = self.name
    slug_candidate = slug_original = slugify(value, allow_unicode=True)
    for i in itertools.count(1):
      if not Tag.objects.filter(slug=slug_candidate).exists():
        break
      slug_candidate = '{}-{}'.format(slug_original, i)

    self.slug = slug_candidate
  
  def save(self, *args, **kwargs):
    if not self.pk:
      self.generate_slug()
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name

class OptionType(models.Model):
  name=models.CharField(max_length=100,null=False)

  def __str__(self):
    return self.name
  

class OptionValue(models.Model):
  value=models.CharField(max_length=100, null=False)
  option_type = models.ForeignKey(OptionType, default=None, on_delete=models.CASCADE, null=True)

  def __str__(self):
    return self.value

  class Meta:
    unique_together = ('value', 'option_type')

class Product(models.Model):
  category = models.ForeignKey(Category, default=None, on_delete=models.CASCADE, null=False)
  option_type = models.ForeignKey(OptionType, default='default', on_delete=models.CASCADE, null=True)
  color = models.CharField(max_length=100, null=False)
  name = models.CharField(max_length=200, null=False)
  description = models.TextField()
  model_number = models.CharField(max_length=100)
  min_order_quantity = models.IntegerField(validators=[MinValueValidator(0)])
  max_order_quantity = models.IntegerField(validators=[MinValueValidator(0)])
  delivery_option = models.CharField(max_length=100, choices=DELIVERY_OPTION_CHOICES, default='Both')
  pricing_option = models.CharField(max_length=200, choices=PRICE_OPTION_CHOICES, default='Fixed Price')
  product_type = models.CharField(max_length=200)
  payment_plan_acceptance_option = models.CharField(max_length=200)
  slug = models.SlugField(null=False, unique=True, editable=False)
  search_tags = models.ManyToManyField(Tag)
  new_arrival = models.BooleanField(default=False)
  is_active = models.BooleanField(default=False)
  approved = models.BooleanField(default=False)
  featured = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now=True)
  updated_at = models.DateTimeField(auto_now=True)

  def display_image(self):
    return self.images()[0] if len(self.images()) > 0 else None

  def get_absolute_url(self):
    kwargs = {
      'slug': self.slug
    }
    return reverse('product-slug-show', kwargs=kwargs)

  def average_rating(self):
    total_rating = 0
    for review in self.review_set.all():
      total_rating += review.rating
    
    return total_rating/self.review_set.all().count()
    
  def images(self):
    images_paths = []
    for attachment in self.attachment_set.filter(attachment_type='Image'):
      if attachment.file and hasattr(attachment.file, 'url'):
        images_paths.append(attachment.file.url)
    return images_paths
  
  def videos(self):
    video_paths = []
    for attachment in self.attachment_set.filter(attachment_type='Video'):
      video_paths.append(attachment.file.url)
    return video_paths
  
  def variants(self):
    return self.variant_set.all()
  
  def reviews(self):
    return self.review_set.all()
    
  def generate_slug(self):
    value = self.name
    slug_candidate = slug_original = slugify(value, allow_unicode=True)
    for i in itertools.count(1):
      if not Product.objects.filter(slug=slug_candidate).exists():
        break
      slug_candidate = '{}-{}'.format(slug_original, i)

    self.slug = slug_candidate
  
  def save(self, *args, **kwargs):
    if not self.pk:
      self.generate_slug()
    super().save(*args, **kwargs)

  def __str__(self):
    return self.name

class Variant(models.Model):
  product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
  option_value = models.ForeignKey(OptionValue, default=None, on_delete=models.CASCADE, null=True)
  stock = models.IntegerField(validators=[MinValueValidator(0)])
  price = models.DecimalField(decimal_places=2, max_digits=9, default=1.0, validators=[MinValueValidator(1.0)])

  class Meta:
    unique_together = ('product', 'option_value')
  
  
class Attachment(models.Model):
  product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
  attachment_type = models.CharField(max_length=200, choices=ATTACHMENT_TYPE_OPTIONS, default='Image')
  file = models.FileField(upload_to='product_attachments', null=True, blank=False)

  def url(self):
    return self.file.url if self.file and hasattr(self.file, 'url') else None
