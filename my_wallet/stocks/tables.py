import django_tables2 as table
from django_tables2.utils import A
from .models import Prices

class PricesTable(table.Table):
    class Meta:
        model = Prices
        fields = ('date_price', 'price')
        attrs = {"class": "table table-light table-striped table-hover shadowing",
                 "thead": {"class": "thead-dark"},
        }
        empty_text = 'No historical data'
