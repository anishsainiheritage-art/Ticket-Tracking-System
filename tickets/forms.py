from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):

    class Meta:
        model = Ticket

        fields = [
            'full_name',
            # 'mobile_number',
            # 'email',
            'department',
            'issue_type',
            'priority',
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

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if not attachment:
            return attachment

        import os
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import InMemoryUploadedFile
        import sys

        ext = os.path.splitext(attachment.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png']:
            try:
                # Read image
                image = Image.open(attachment)
                
                # Convert to RGB if needed (e.g. for PNGs with transparency)
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                
                # Compress into a buffer
                output = BytesIO()
                image.save(output, format='JPEG', quality=60, optimize=True)
                output.seek(0)
                
                # Create a new Django InMemoryUploadedFile
                new_name = os.path.splitext(attachment.name)[0] + '.jpg'
                attachment = InMemoryUploadedFile(
                    output,
                    attachment.field_name,
                    new_name,
                    'image/jpeg',
                    sys.getsizeof(output),
                    None
                )
            except Exception:
                # If anything fails (e.g., corrupt image), fail gracefully and return original
                pass
                
        return attachment