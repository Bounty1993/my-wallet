from django.test import TestCase, Client
from ..views import DownloadCsvExcel

class TestDownloadCsvExcel(TestCase):
    def setUp(self):
        self.request = DownloadCsvExcel()

    def test_csv_response(self):
        data = self.request.download_csv()