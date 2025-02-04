from django import forms
from .models import *

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
            'token_symbol': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., BTC'}),
            'token_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bitcoin'}),
            'exchange': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Binance'}),
        }