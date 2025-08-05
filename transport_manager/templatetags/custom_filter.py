from django import template

register = template.Library()


@register.filter
def direction(value):
    if value:
        return "From DSC"
    else:
        return "To DSC"
