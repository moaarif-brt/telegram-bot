from django import forms
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Enter your registered email",
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not registered.")
        return email

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your New Password'}), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your New Password again'}), label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data



class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
        label="Password"
    )


class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = ['token_symbol', 'token_name', 'exchange']
        labels = {
            'token_symbol': 'Token Symbol',
            'token_name': 'Token Name',
            'exchange': 'Exchange Platform',
        }
        widgets = {
            'token_symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., BTC', 'style': 'text-transform: uppercase;'}),
            'token_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bitcoin', 'style': 'text-transform: uppercase;'}),
            'exchange': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Binance', 'style': 'text-transform: uppercase;'}),
        }
