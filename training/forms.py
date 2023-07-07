from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from hubble import models
from hubble.models import Assessment


class TimelineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["team"].empty_label = "Select a Team"
        self.fields["name"].validators.append(MinLengthValidator(3))

    def clean_is_active(self):
        """
        This function checks if a team already has an active template and raises a validation error if
        it does.
        """
        if self.cleaned_data.get("team", None) and (self.cleaned_data["is_active"]):
            query = models.Timeline.objects.filter(
                team=self.cleaned_data["team"], is_active=True
            ).values("id")
            if (len(query)) and (query[0]["id"] != (self.instance.id)):
                raise ValidationError("Team already has an active template.")

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
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "checkbox_active cursor-pointer block border border-primary-dark-30 rounded-md w-4 mr-3 focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                }
            ),
        }


class TimelineTaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].validators.append(MinLengthValidator(3))

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


class BatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].validators.append(MinLengthValidator(3))

    class Meta:
        model = models.Batch
        fields = ("name",)

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "Batch Name...",
                }
            )
        }


class SubBatchForm(forms.ModelForm):
    primary_mentor_id = forms.ModelChoiceField(
        queryset=models.User.objects.filter(is_employed=True)
    )

    secondary_mentor_id = forms.ModelChoiceField(
        queryset=models.User.objects.filter(is_employed=True)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["team"].empty_label = "Select a Team"
        if self.data.get("team", None):
            self.fields["team"].widget.attrs["initialValue"] = self.data.get(
                "team", None
            )

        self.fields["primary_mentor_id"].empty_label = "Select a Primary Mentor"
        if self.data.get("primary_mentor_id", None):
            self.fields["primary_mentor_id"].widget.attrs[
                "initialValue"
            ] = self.data.get("primary_mentor_id", None)

        self.fields["secondary_mentor_id"].empty_label = "Select a Secondary Mentor"
        if self.data.get("secondary_mentor_id", None):
            self.fields["secondary_mentor_id"].widget.attrs[
                "initialValue"
            ] = self.data.get("secondary_mentor_id", None)

        self.fields["name"].validators.append(MinLengthValidator(3))
        self.fields["primary_mentor_id"].label = "Primary Mentor"
        self.fields["secondary_mentor_id"].label = "Secondary Mentor"

        if kwargs.get("instance"):
            instance = kwargs.get("instance")
            self.fields["team"].widget.attrs["initialValue"] = instance.team
            self.fields["primary_mentor_id"].widget.attrs[
                "initialValue"
            ] = instance.primary_mentor_id
            self.fields["secondary_mentor_id"].widget.attrs[
                "initialValue"
            ] = instance.secondary_mentor_id

    class Meta:
        model = models.SubBatch
        fields = (
            "name",
            "team",
            "start_date",
            "timeline",
            "primary_mentor_id",
            "secondary_mentor_id",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 mt-2.5 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 bg-transparent w-250 ",
                    "placeholder": "Batch Name...",
                }
            ),
            "team": forms.Select(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 dropdown_select bg-transparent w-250",
                    "placeholder": "Select Team...",
                }
            ),
            "start_date": forms.DateInput(
                attrs={
                    "class": "block border border-primary-dark-30 rounded-md mt-2.5 w-64 focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 bg-transparent w-250 start_date_input",
                    "placeholder": "Start Date...",
                }
            ),
            "timeline": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 mt-2.5 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 bg-transparent w-250 timeline-input",
                }
            ),
            "primary_mentor_id": forms.Select(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 dropdown_select bg-transparent w-250",
                    "placeholder": "Primary Mentor...",
                }
            ),
            "secondary_mentor_id": forms.Select(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 dropdown_select bg-transparent w-250",
                    "placeholder": "Secondary Mentor...",
                }
            ),
        }


class AddInternForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["college"].validators.append(MinLengthValidator(3))
        self.fields["user_id"].empty_label = "Select a Trainee"

    user_id = forms.ModelChoiceField(
        queryset=(
            models.User.objects.exclude(intern_details__isnull=False).filter(
                is_employed=False
            )
        ),
        label="User",
    )

    class Meta:
        model = models.InternDetail
        fields = ("user_id", "college")

        widgets = {
            "college": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "College name...",
                }
            ),
            "user_id": forms.Select(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2 dropdown_select bg-transparent w-250",
                    "placeholder": "Trainee...",
                }
            ),
        }


class SubBatchTimelineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].validators.append(MinLengthValidator(3))

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
                "placeholder": "Days...",
            }
        ),
        validators=[validate_days],
    )
    order = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                "placeholder": "Order...",
                "required": False,
            }
        ),
    )

    class Meta:
        model = models.SubBatchTaskTimeline
        fields = ("name", "days", "present_type", "task_type", "order")

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "Task Name...",
                }
            ),
            "present_type": forms.RadioSelect(),
            "task_type": forms.RadioSelect(),
        }


class InternScoreForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ("score", "is_retry", "comment")

        widgets = {
            "score": forms.NumberInput(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                    "placeholder": "Enter score...",
                }
            ),
            "is_retry": forms.CheckboxInput(
                attrs={
                    "class": "checkbox_active cursor-pointer block border border-primary-dark-30 rounded-md w-4 mr-3 focus:outline-none focus:ring-transparent focus:ring-offset-0 h-9 p-2",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full block border border-primary-dark-30 rounded-md mt-2.5 w-64 focus:outline-none focus:ring-transparent focus:ring-offset-0 h-20 p-2 ",
                    "placeholder": "Enter comment...",
                }
            ),
        }