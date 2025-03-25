from django import forms

from agro.models import Cart, Complain, Order, ProductItem


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ['title', 'price', 'category', 'unit', 'quantity', 'description', 'image', 'post_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ComplainForm(forms.ModelForm):
    class Meta:
        model = Complain
        fields = ['subject', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'zipcode']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'phone': forms.TextInput(attrs={'required': True, 'pattern': '[0-9]{10}', 'title': 'Phone number must be 10 digits'}),
            'email': forms.EmailInput(attrs={'required': False}),
            'pincode': forms.TextInput(attrs={'pattern': '[0-9]{6}', 'title': 'PIN code must be 6 digits'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide zipcode field as we'll use pincode value for both
        self.fields['zipcode'].widget = forms.HiddenInput()
        self.fields['zipcode'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode:
            raise forms.ValidationError("PIN code is required.")
        if not pincode.isdigit():
            raise forms.ValidationError("PIN code must contain only digits.")
        if len(pincode) != 6:
            raise forms.ValidationError("PIN code must be exactly 6 digits.")
        return pincode

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 100, 'class': 'form-control'})
        }
        