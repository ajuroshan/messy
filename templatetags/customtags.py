from django import template

register = template.Library()

@register.filter(is_safe=True)
def length_is(value, arg):
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False