from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import User_info


class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('first_name','last_name','username','email')

class UserInfo(forms.ModelForm):
    profile_pic = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))
    
    class Meta:
        model = User_info
        fields = ('profile_pic', 'gender', 'address', 'phone')
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}', 'title': 'Phone number must be 10 digits'})
        }


class UserFLEname(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')