from django.test import TestCase
from .models import Profile


class ProfileTest(TestCase):

    def setUp(self):
        Profile.objects.create(name='Bartosz')

    def test_profile_exists(self):
        user = Profile.objects.filter(name='Bartosz')
        self.assertTrue(user.exists())

    def test_profile_data(self):
        user = Profile.objects.get(name='Bartosz')
        self.assertEqual(user.name, 'Bartosz')
