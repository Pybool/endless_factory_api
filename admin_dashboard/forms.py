from django import forms
from django.forms import ChoiceField
from products.models import Category, Filters, Tag, Product, Variant, Attachment, OptionType, OptionValue
from accounts.models import User, Address, CreditCard


class CategoryForm(forms.ModelForm):
 
  def CATEGORY_CHOICES():
    
      categories_tuple = [('-1','----',)]
      categories = Category.objects.all().values_list('id','name')
      for category in list(categories):
          padded_cat = category
          categories_tuple.append(padded_cat)
      return tuple(categories_tuple) 
      
  CHOICES = CATEGORY_CHOICES()
  parent = forms.ChoiceField(widget=forms.Select,choices=CHOICES)
  
  class Meta:
    model = Category
    fields = ('parent','name', 'description', 'image')
        
class TagForm(forms.ModelForm):
  class Meta:
    model = Tag
    fields = ('name',)
    
class FiltersForm(forms.ModelForm):
  class Meta:
    model = Filters
    fields = ('name','filter_type','filter_variants')

class OptionValueForm(forms.ModelForm):
  class Meta:
    model = OptionValue
    fields = ('option_type', 'value')

class OptionTypeForm(forms.ModelForm):
  class Meta:
    model = OptionType
    fields = ('name', )

class ProductForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = ('title', 'description', 'is_active', 'model_number', 'min_order_quantity', 'max_order_quantity', 'delivery_option', 'initial_stock', 'current_stock', 'search_tags', 'category', 'option_type', 'approved', 'featured')

class VariantForm(forms.ModelForm):
  class Meta:
    model = Variant
    fields = ('stock', 'price', 'product', 'option_value')

class AttachmentForm(forms.ModelForm):
  class Meta:
    model = Attachment
    fields = ('attachment_type', 'file', 'product')

class UserProfileForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ('email', 'name', 'password', 'user_type', 'country')

class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ('email', 'name', 'user_type', 'password', 'company_name', 'country', 'company_mailing_address', 'company_description', 'tax_id_number', 'phone_number', 'entity_type', 'payment_acceptance_type', 'bank_info', 'contact_preferences', 'number_of_employees', 'year_founded', 'gross_annual_revenue')

class AddressForm(forms.ModelForm):
  class Meta:
    model = Address
    fields = ('first_name', 'last_name', 'line_1', 'line_2', 'city', 'state', 'zipcode', 'country')

class CreditCardForm(forms.ModelForm):
  class Meta:
    model = CreditCard
    fields = ('card_number', 'exp_month', 'exp_year', 'name_on_card')


