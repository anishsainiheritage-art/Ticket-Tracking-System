from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            'full_name',
            'mobile_number',
            'email',
            'department',
            'issue_type',
            'priority',
            'subject',
            'description',
            'attachment',
        ]

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')

        if not mobile.isdigit():
            raise forms.ValidationError(
                "Mobile number must contain digits only."
            )

        if len(mobile) != 10:
            raise forms.ValidationError(
                "Mobile number must be 10 digits."
            )

        return mobile