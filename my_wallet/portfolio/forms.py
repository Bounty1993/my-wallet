from django import forms
from .models import Asset
from .models import Portfolio, Transaction
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Column, Fieldset, Layout, Field
from crispy_forms.bootstrap import TabHolder, Tab


class NewPortfolioForm(forms.ModelForm):

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Staraj się zmieścić w 250 słowach'
    )

    class Meta:
        model = Portfolio
        fields = (
            'name',
            'description',
            'beginning_cash',
            'is_visible'
        )


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'stocks',
            'number',
        )
