from django.contrib import admin
from .models import Product, Tag, Attachment, Category, OptionType, OptionValue
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Attachment)
admin.site.register(OptionType)