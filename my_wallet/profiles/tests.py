from django.test import TestCase
from django.urls import reverse, resolve
from .models import Profile
from .views import MyProfileCreation


class ProfileModelTest(TestCase):

    def setUp(self):
        Profile.objects.create(name='Bartosz')

    def test_profile_exists(self):
        user = Profile.objects.filter(name='Bartosz')
        self.assertTrue(user.exists())

    def test_profile_data(self):
        user = Profile.objects.get(name='Bartosz')
        self.assertEqual(user.name, 'Bartosz')


class ProfileViewTest(TestCase):

    def setUp(self):
        url = reverse('profiles:signup')
        self.response = self.client.get(url)

    def test_status_response(self):
        self.assertEquals(self.response.status_code, 200)

    def test_profile_url_revolves_profile_view(self):
        view = resolve('/register/signup/')
        self.assertEquals(view.func.view_class, MyProfileCreation)


