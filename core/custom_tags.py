from django import template
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from . import constants

register = template.Library()


@register.simple_tag(takes_context=True)
def set_active(context, names):
    current_route_name = resolve(
        context["request"].path_info
    ).route  # Get the url of the current request
    names = names.split(", ")
    for name in names:
        if (
            current_route_name == name
            or (name.endswith("/*"))
            and (
                current_route_name.startswith(name.replace("/*", ""))
                or current_route_name == name.replace("/*", "")
            )
        ):
            return "sidebar-active"
    return ""


@register.simple_tag
def get_constant(name):
    return getattr(constants, name)


@register.filter()
def replace_spaces(value):
    return value.replace(" ", "_")


@register.filter()
def show_field_errors(field):
    if field.errors:
        error_message = ""
        for error in field.errors:
            error_message = strip_tags(error)
        return mark_safe(
            '<span id="validation-error" class="ajax-error form_errors text-red-600">{}</span>'.format(
                error_message
            )
        )
    else:
        return ""


@register.filter()
def show_non_field_errors(error):
    if error:
        return mark_safe(
            '<span id="validation-error" class="ajax-error form_errors text-red-600">{}</span>'.format(
                error
            )
        )
    else:
        return ""


@register.filter()
def show_label(field):
    if field.field.required:  # Check the field is required or not
        required = '<span class="text-red-600">*</span>'
    else:
        required = ""
    return mark_safe(
        '<label for="{}" class="mb-3.6 text-sm text-dark-black-50">{} {}</label>'.format(
            field.label.lower().replace(" ", "_"), field.label, required
        )
    )
