from django import template
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from . import constants

register = template.Library()


@register.simple_tag(takes_context=True)
def set_active(context, names):
    current_route_name = resolve(context["request"].path_info).url_name
    tuple_name = tuple(names.split(", "))
    if current_route_name in tuple_name:
        return "active"


@register.simple_tag
def get_constant(name):
    return getattr(constants, name)


@register.filter()
def show_field_errors(field):
    if field.errors:
        error_message = ""
        for error in field.errors:
            error_message = strip_tags(error)
        return mark_safe('<span class="text-danger">{}</span>'.format(error_message))
    else:
        return ""


@register.filter()
def show_non_field_errors(error):
    if error:
        error_message = strip_tags(error)
        return mark_safe(
            '<div class="alert alert-danger"><p><span class="fe fe-alert-triangle fe-16 mr-2"></span>{}'
            "</p></div>".format(error_message)
        )
    else:
        return ""


@register.filter()
def show_label(field):
    if field.field.required:
        required = '<span class="mandatory">*</span>'
    else:
        required = ""
    return mark_safe('<label for="name">{} {}</label>'.format(field.label, required))
