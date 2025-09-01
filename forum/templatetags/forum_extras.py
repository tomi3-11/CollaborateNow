from django import template
from django.utils.timesince import timesince
from datetime import datetime, timezone

register = template.Library()

@register.filter
def simple_naturaltime(value):
    """
    Returns a simplified natural time like '2 weeks ago' 
    instead of '2 weeks, 3 days'.
    """
    
    if not value:
        return ""
    
    now = datetime.now(timezone.utc)
    delta = timesince(value, now)
    
    # Keep only the first unit (e.g., '2 weeks')
    first_unit = delta.split(", ")[0]
    return f"{first_unit} ago"