from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def book_status(available_copies):
    try:
        available = int(available_copies)
    except (TypeError, ValueError):
        available = 0
    if available > 0:
        return mark_safe(f'<span class="badge text-bg-success">Available ({available})</span>')
    return mark_safe('<span class="badge text-bg-danger">Fully Borrowed</span>')
