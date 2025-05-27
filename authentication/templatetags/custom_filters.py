from django import template

register = template.Library()


@register.filter
def first_name(name):
    names = name.split()
    if names[0] == "Md." or names[0] == "MD.":
        return names[1]
    else:
        return names[0]
