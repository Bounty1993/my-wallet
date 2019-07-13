from django import forms
from django.forms import ValidationError

from .models import Asset, Portfolio, Transaction


class NewPortfolioForm(forms.ModelForm):

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        help_text='Staraj się zmieścić w 250 słowach',
        label='Opis'
    )

    class Meta:
        model = Portfolio
        fields = (
            'name',
            'description',
            'beginning_cash',
            'is_visible'
        )
        help_text = {
            'beginning_cash': 'Kwota powinna być między 100 a 10 milionów złotych',
        }

    def clean_beginning_cash(self):
        beginning_cash = self.cleaned_data['beginning_cash']
        if beginning_cash < 1000:
            msg = 'Początkowa gotówka musi wynosić co najmniej 1000'
            raise ValidationError(msg)
        if beginning_cash > 10_000_000:
            msg = 'Maksymalna wartośc początkowej gotówki to 10 milionów złotych'
            raise ValidationError(msg)
        return beginning_cash


class TransactionForm(forms.ModelForm):
    price = forms.DecimalField(widget=forms.HiddenInput())

    class Meta:
        model = Transaction
        fields = (
            'price',
            'stocks',
            'number',
            'kind',
            'portfolio',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kind'].widget = forms.HiddenInput()
        self.fields['portfolio'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        print("in clean", cleaned_data)
        portfolio = cleaned_data['portfolio']

        kind = cleaned_data['kind']
        stocks = cleaned_data['stocks']
        number = cleaned_data['number']
        price = cleaned_data['price']
        if kind == 'buy':
            total_value = price * number
            if portfolio.cash < total_value:
                raise ValidationError('Środki finansowe są niewystarczające')
        else:
            stocks_in_portfolio = portfolio.assets.filter(stocks=stocks)
            if stocks_in_portfolio.count() == 0:
                raise ValidationError('Nie masz tych akcji w portfelu')
            num_of_stocks = stocks_in_portfolio.first().sum_number
            if num_of_stocks < number:
                raise ValidationError('Nie możesz sprzedać więcej akcji niż posiadasz')
