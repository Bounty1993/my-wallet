from django import template
from django.utils.html import format_html
register = template.Library()


@register.filter
def color_field(value):
    if value:
        value = round(value, 2)
        if value < 0:
            return format_html(f'<span class=falling>{value}USD</span>')
        elif value > 0:
            return format_html(f'<span class=rising>{value}USD</span>')
    return value


@register.filter
def color_percent(value, digits):
    value = round(value, digits) if value else value
    if value:
        if value < 0:
            return format_html(f'<span class=falling>{value}%</span>')
        elif value > 0:
            return format_html(f'<span class=rising>{value}%</span>')
    return value
