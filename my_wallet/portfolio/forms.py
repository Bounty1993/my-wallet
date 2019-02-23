from django import forms
from .models import Asset
from .models import Portfolio

class NewPortfolioForm(forms.ModelForm):

    class Meta:
        model = Portfolio
        fields = (
            'name',
            'description',
            'beginning_cash',
            'cash',
            'is_visible'
        )
