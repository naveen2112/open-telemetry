from django import template
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from . import constants

register = template.Library()


@register.simple_tag(takes_context=True)
def set_active(context, names):
    current_route_name = resolve(context["request"].path_info).route
    names = names.split(", ")
    for name in names:
        if "/*" in name:
            if current_route_name.startswith(name.replace("*", "")):
                return "active"
        elif current_route_name.startswith(name):
            return "active"
    return ""


@register.simple_tag
def get_constant(name):
    return getattr(constants, name)