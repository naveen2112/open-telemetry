from django import forms
from hubble import models
from django.core.exceptions import ValidationError


class TimelineForm(forms.ModelForm):
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                "type": "checkbox",
                "class": "checkbox_active cursor-pointer block border border-primary-dark-30 rounded-md w-4 mr-3 focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
            }
        )
    )

    class Meta:
        model = models.Timeline
        fields = ("name", "team", "is_active")

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "Timeline name...",
                }
            ),
            "team": forms.Select(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 dropdown_select",
                    "placeholder": "Select Team...",
                }
            ),
        }


class TimelineTaskForm(forms.ModelForm):
    def validate_days(value):
        """
        The function validates that a given value is greater than 0 and a multiple of 0.5, otherwise it
        raises a validation error.
        """
        if value <= 0:
            raise ValidationError("Value must be greater than 0")
        if value % 0.5 != 0: 
            raise ValidationError("Value must be a multiple of 0.5")

    days = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                "placeholder": "No of days...",
            }
        ),
        validators=[validate_days],
    )

    class Meta:
        model = models.TimelineTask
        fields = ("name", "days", "present_type", "task_type")

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "Timeline name...",
                }
            ),
            "present_type": forms.RadioSelect(),
            "task_type": forms.RadioSelect(),
        }
