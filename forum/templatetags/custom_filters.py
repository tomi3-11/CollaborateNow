from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime as django_naturaltime
import re

register = template.Library()

@register.filter
def clean_naturaltime(value):
    """
    Return a clean relative time like '1 day ago' or 'just now'.
    """
    if not value:
        return
    
    result = django_naturaltime(value)

    if not isinstance(result, str):
        return result

   # Extract the first time unit (e.g., '1 day')
    match = re.match(r'(\d+ \w+)', result)

    if match:
        return match.group(1) + " ago"
    
    return result
    