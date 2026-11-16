from django import forms
from django.utils import timezone

from .models import Report


class ReportCreateForm(forms.ModelForm):

    latitude = forms.FloatField(
        widget=forms.HiddenInput()
    )

    longitude = forms.FloatField(
        widget=forms.HiddenInput()
    )

    location_accuracy = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )

    location_name = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    location_source = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Report

        fields = [
            "type",
            "title",
            "category",
            "description",
            "occurred_at",
            "phone_number",
        ]

        widgets = {
            "type": forms.RadioSelect(),

            "title": forms.TextInput(
                attrs={
                    "placeholder": "e.g. Black iPhone 13",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": (
                        "Describe the item and any useful identifying details..."
                    ),
                }
            ),

            "occurred_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "type": "tel",
                    "placeholder": "+2348012345678",
                    "autocomplete": "tel",
                }
            ),
        }

    def clean_occurred_at(self):
        occurred_at = self.cleaned_data["occurred_at"]

        if occurred_at > timezone.now():
            raise forms.ValidationError(
                "The lost/found time cannot be in the future."
            )

        return occurred_at

    def clean(self):
        cleaned_data = super().clean()

        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")

        if latitude is None or longitude is None:
            raise forms.ValidationError(
                "Please select the location where the item was lost or found."
            )

        return cleaned_data

class ReportUpdateForm(ReportCreateForm):

    class Meta(ReportCreateForm.Meta):
        fields = [
            "title",
            "category",
            "description",
            "occurred_at",
            "phone_number",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.location:
            self.initial.setdefault(
                "latitude",
                self.instance.location.y,
            )
            self.initial.setdefault(
                "longitude",
                self.instance.location.x,
            )
            self.initial.setdefault(
                "location_name",
                self.instance.location_name,
            )
            self.initial.setdefault(
                "location_accuracy",
                self.instance.location_accuracy,
            )
            self.initial.setdefault(
                "location_source",
                self.instance.location_source,
            )