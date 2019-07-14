from django.test import TestCase
from django.urls import reverse


class CoreViewTest(TestCase):
    def test_status_code(self):
        url = reverse('core:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
