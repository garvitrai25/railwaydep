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
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'state', 'pincode', 'zipcode', 'payment_method']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide zipcode field as we'll use pincode value for both
        self.fields['zipcode'].widget = forms.HiddenInput()
        self.fields['zipcode'].required = False

class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 100, 'class': 'form-control'})
        }
        