from myaccount.models import Account
from django import forms
from .models import PrivateMessage

class FormMessage(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['message']
