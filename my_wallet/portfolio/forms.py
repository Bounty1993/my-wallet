from django import forms
from .models import Asset
from .models import Portfolio, Transaction
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Column, Fieldset, Layout, Field
from crispy_forms.bootstrap import TabHolder, Tab


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Buy',
                    Field('stocks', css_class='my-field'),
                    'number',
                ),
                Tab(
                    'Sell',
                    'stocks',
                    'number',
                )
            )
        )

    class Meta:
        model = Transaction
        fields = (
            'stocks',
            'number',
        )
