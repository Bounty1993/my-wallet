from django.test import TestCase, Client
from django.urls import resolve
from ..views import StocksListView

"""
class TestDownloadCsvExcel(TestCase):
    def setUp(self):
        self.request = DownloadCsvExcel()

    def test_csv_response(self):
        data = self.request.download_csv()
"""

class TestStocksListView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_resolve_url_class(self):
        found = resolve('/stocks/')
        self.assertEquals(StocksListView.__name__, found.func.__name__)

    def test_response_code(self):
        url = '/stocks/'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
