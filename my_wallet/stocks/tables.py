import math

from django.utils.html import format_html
import django_tables2 as table

from .models import Dividends, Prices


class PricesTable(table.Table):

    def color_change(self, value):
        if value < 0:
            return format_html(f'<div class="falling">{value}</div>')
        elif value > 0:
            return format_html(f'<div class="rising">{value}</div>')
        return value

    def render_change(self, value):
        value = round(value, 2)
        return self.color_change(value)

    def render_percent_change(self, value):
        value = round(value, 3)
        return self.color_change(value)

    class Meta:
        model = Prices
        fields = ('date_price', 'open', 'price', 'change', 'percent_change', 'volume')
        empty_text = 'No historical data'
        attrs = {
            'class': 'main_table',
            'td': {'class': 'tab-cell'}
        }
        row_attrs = {
            'class': 'custom_rows'
        }
        template_name = 'table_draft.html'


class Quarter(table.Column):
    def render(self, record):
        if record.record:
            present_quarter = math.ceil(record.record.month/3)
            return f'{present_quarter}Q {record.record.year}'
        return None


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
