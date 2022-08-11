from django import template
from endless_admin.translations import get_translations
register = template.Library()

def translate(text, locale):
  return get_translations(text, locale)

register.filter('translate', translate)
  