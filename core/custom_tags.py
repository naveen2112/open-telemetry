from django import template
from django.urls import resolve
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from . import constants

register = template.Library()


@register.simple_tag(takes_context=True)
def set_active(context, names):
    current_route_name = resolve(context["request"].path_info).route
    names = names.split(", ")
    for name in names:
        if (current_route_name == name or (name.endswith("/*"))
            and (current_route_name.startswith(name.replace("/*", ""))
                or current_route_name == name.replace("/*", "")
            )
        ):
            return "sidebar-active"
    return ""


@register.simple_tag
def get_constant(name):
    return getattr(constants, name)


@register.filter()
def show_field_errors(field):
    if field.errors:
        error_message = ''
        for error in field.errors:
            error_message = strip_tags(error)
        return mark_safe('<span id="reason_error" class="ajax-error text-red-600">{}</span>'.format(error_message))
    else:
        return ""


@register.filter()
def show_non_field_errors(error):
    if error:
        error_message = strip_tags(error)
        return mark_safe('<div class="alert alert-danger"><p><span class="fe fe-alert-triangle fe-16 mr-2"></span>{}'
                         '</p></div>'.format(error_message))
    else:
        return ""
    

@register.filter()
def show_label(field):
    if isinstance(field, str):
        # Convert the field parameter to a form field object
        field = template.Variable(field).resolve({})
    if field.field.required: 
        required = '<span class="text-red-600">*</span>'
    else:
        required = ''
    return mark_safe('<label for="{}" class="mb-3.6 text-sm text-dark-black-50">{} {}</label>'.format(field.label, field.label, required))


@register.filter
def add_id(field):
    """
    Adds an ID attribute to a form field.
    """
    field_id = f"update_{field.name}"
    return format_html('{}', field.as_widget(attrs={'id': field_id}))

