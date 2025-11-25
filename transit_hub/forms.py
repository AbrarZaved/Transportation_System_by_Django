from django import forms
from .models import Driver, Bus, Helper  # Make sure to import Bus and Helper model


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            "name",
            "phone_number",
            "license_number",
            "license_expiry",
            "license_class",
            "license_country",
            "license_issued",
            "license_photo",
            "driver_photo",
            "driver_status",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                    "placeholder": "e.g., Md. Karim Rahman",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                    "placeholder": "e.g., +88017XXXXXXXX",
                }
            ),
            "license_number": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                    "placeholder": "e.g., DL-ABC-12345",
                }
            ),
            "license_expiry": forms.DateInput(
                attrs={
                    "type": "date",  # Important for date picker
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                }
            ),
            "license_class": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                    "placeholder": "e.g., Light Vehicle",
                }
            ),
            "license_country": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                    "placeholder": "e.g., Bangladesh",
                }
            ),
            "license_issued": forms.DateInput(
                attrs={
                    "type": "date",  # Important for date picker
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-green-500 focus:border-green-500 text-sm",
                }
            ),
            "license_photo": forms.ClearableFileInput(
                attrs={
                    "class": "mt-1 w-full text-gray-800 text-sm file:mr-2 file:py-1.5 file:px-2 file:rounded-md file:border-0 file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer",
                    "accept": "image/*",  # Ensures only image files can be selected
                }
            ),
            "driver_photo": forms.ClearableFileInput(
                attrs={
                    "class": "mt-1 w-full text-gray-800 text-sm file:mr-2 file:py-1.5 file:px-2 file:rounded-md file:border-0 file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer",
                    "accept": "image/*",  # Ensures only image files can be selected
                }
            ),
            "driver_status": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded",  # Basic Tailwind for checkbox
                }
            ),
        }


class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            "bus_name",
            "bus_tag",
            "bus_number",
            "bus_model",
            "bus_capacity",
            "bus_photo",
            "bus_status",
        ]
        widgets = {
            "bus_name": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-blue-500 focus:border-blue-500 text-sm",
                    "placeholder": "e.g., DIU-Bus-A",
                }
            ),
            "bus_tag": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-blue-500 focus:border-blue-500 text-sm",
                    "placeholder": "e.g., DAFFODIL",
                }
            ),
            "bus_number": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-blue-500 focus:border-blue-500 text-sm",
                    "placeholder": "e.g., Dhaka-Metro-B-11-XXXX",
                }
            ),
            "bus_model": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-blue-500 focus:border-blue-500 text-sm",
                    "placeholder": "e.g., Hino AK1J",
                }
            ),
            "bus_capacity": forms.NumberInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-blue-500 focus:border-blue-500 text-sm",
                    "placeholder": "e.g., 40",
                }
            ),
            "bus_photo": forms.ClearableFileInput(
                attrs={
                    "class": "mt-1 w-full text-gray-800 text-sm file:mr-2 file:py-1.5 file:px-2 file:rounded-md file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer",
                    "accept": "image/*",  # Ensures only image files can be selected
                }
            ),
            "bus_status": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded",  # Basic Tailwind for checkbox
                }
            ),
        }


class HelperForm(forms.ModelForm):
    class Meta:
        model = Helper
        fields = [
            "name",
            "phone_number",
            "helper_photo",
            "helper_status",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-yellow-500 focus:border-yellow-500 text-sm",
                    "placeholder": "e.g., Md. Rahim Uddin",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "mt-1 w-full border border-gray-300 rounded-md px-2 py-1.5 text-gray-800 focus:ring-yellow-500 focus:border-yellow-500 text-sm",
                    "placeholder": "e.g., +88017XXXXXXXX",
                }
            ),
            "helper_photo": forms.ClearableFileInput(
                attrs={
                    "class": "mt-1 w-full text-gray-800 text-sm file:mr-2 file:py-1.5 file:px-2 file:rounded-md file:border-0 file:font-semibold file:bg-yellow-50 file:text-yellow-700 hover:file:bg-yellow-100 cursor-pointer",
                    "accept": "image/*",  # Ensures only image files can be selected
                }
            ),
            "helper_status": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300 rounded",  # Basic Tailwind for checkbox
                }
            ),
        }
