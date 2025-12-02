from django import forms
from authentication.models import SupportTicket


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "category", "description", "image"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "Brief description of your issue",
                }
            ),
            "category": forms.Select(
                attrs={"class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent  ",
                    "rows": "6",
                    "placeholder": "Please provide detailed information...",
                }
            ),
            "image": forms.FileInput(
                attrs={"class": "w-full mt-1 border border-gray-300 rounded px-4 py-2"}
            ),
        }
