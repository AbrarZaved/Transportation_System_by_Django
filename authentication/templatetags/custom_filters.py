from django import template

register = template.Library()


@register.filter
def first_name(name):
    tags = ["mst.", "most.", "md.", "md"]
    names = name.lower().split(" ")
    if names[0] in tags:
        return names[1].title()
    return names[0].title()
