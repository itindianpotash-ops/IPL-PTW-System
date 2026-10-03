from django import forms

from .models import Permit


class PermitForm(forms.ModelForm):

    class Meta:
        model = Permit

        fields = [
            "permit_type",
            "location",
            "work_description",
            "contractor_name",
            "workers",
            "work_start",
            "work_end",
        ]

        widgets = {
            "work_description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                }
            ),

            "workers": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": (
                        "Enter one worker name per line"
                    ),
                }
            ),

            "work_start": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),

            "work_end": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            if not isinstance(
                field.widget,
                (
                    forms.Textarea,
                    forms.DateTimeInput,
                ),
            ):
                field.widget.attrs["class"] = "form-control"


class ReviewForm(forms.Form):

    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
            }
        ),
    )
