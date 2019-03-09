import django_tables2 as table
from django_tables2.utils import A
import math
from .models import Prices, Dividends


class PricesTable(table.Table):
    class Meta:
        model = Prices
        fields = ('date_price', 'price')
        attrs = {"class": "table table-light table-striped table-hover shadowing",
                 "thead": {"class": "thead-dark"},
        }
        empty_text = 'No historical data'


class Quarter(table.Column):
    def render(self, record):
        present_quarter = math.ceil(record.record.month/3)
        return f'{present_quarter}Q {record.record.year}'


class DividendTable(table.Table):
    quarter = Quarter(empty_values=())

    class Meta:
        model = Dividends
        empty_text = 'No data about dividends'
        fields = ('record', 'payment', 'amount')
        sequence = ('quarter', 'record', 'payment', 'amount')
        attrs = {
            'class': 'main_table',
            'td': {'class': 'tab-cell'}
        }
        row_attrs = {
            'class': 'custom_rows'
        }

        template_name = 'table_draft.html'
