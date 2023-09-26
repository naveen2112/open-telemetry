"""
Module containing custom template tags and filters for the project.
"""
from django import template
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from . import constants

register = template.Library()


@register.simple_tag(takes_context=True)
def set_active(context, names):
    """
    Determines the active state of a sidebar item based on the current route
    name and  returns the CSS class 'sidebar-active'
    """
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
    """
    Retrieves a constant value from the 'constants' module based on
    the provided name
    """
    return getattr(constants, name)


@register.filter()
def replace_spaces(value):
    """
    Replaces spaces in a string with underscores
    """
    return value.replace(" ", "_")


@register.filter()
def show_field_errors(field):
    """
    Returns an HTML representation of the error message for a
    field with custom styling
    """
    if field.errors:
        error_message = ""
        for error in field.errors:
            error_message = strip_tags(error)
        return mark_safe(
            f'<span id="validation-error" class="ajax-error form_errors\
                text-red-600">{error_message}</span>'
        )
    return ""


@register.filter()
def show_non_field_errors(error):
    """
    Returns an HTML representation of the error message for a
    non-field with custom styling
    """
    if error:
        return mark_safe(
            f'<span id="validation-error" class="ajax-error form_errors\
                text-red-600">{error}</span>'
        )
    return ""


@register.filter()
def show_label(field):
    """
    Returns an HTML representation of the label with custom styling
    """
    required = ""
    if field.field.required:  # Check the field is required or not
        required = '<span class="text-red-600">*</span>'
    else:
        required = ""
    if field.field.widget.__class__.__name__ == "CheckboxInput":
        return mark_safe(
            f'<label for="id_{field.label.lower().replace(" ", "_")}" \
                class="mb-3.6 text-sm text-dark-black cursor-pointer"> \
                    {field.label}</label>'  # pylint:disable=C0301
        )
    return mark_safe(
        f'<label for="{field.label.lower().replace(" ", "_")}" \
            class="mb-3.6 text-sm text-dark-black-50">{field.label} {required}</label>'
    )
