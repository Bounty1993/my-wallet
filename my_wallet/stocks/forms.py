from django import forms
from .models import Stocks


class NewStockForm(forms.ModelForm):
    class Meta:
        model = Stocks
        fields = ['ticker']
