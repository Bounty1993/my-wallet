from django import forms
from .models import Asset
from .models import Portfolio, Transaction


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


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = (
            'stocks',
            'number',
        )
