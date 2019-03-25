from django.test import TestCase
from django.urls import reverse, resolve
from .models import Profile
from .views import MyProfileCreationView
from .forms import ProfileCreationForm


class ProfileModelTest(TestCase):

    def setUp(self):
        self.my_user = Profile.objects.create_user(
            username='Bartosz',
            password='Tester123',
            email='bartosz@example.pl'
        )

    def test_profile_exists(self):
        user = Profile.objects.filter(username='Bartosz')
        self.assertTrue(user.exists())

    def test_profile_data(self):
        user = Profile.objects.get(username='Bartosz')
        self.assertEqual(user.username, 'Bartosz')
        self.assertEqual(user.email, 'bartosz@example.pl')

    def test_profile_full_name(self):
        self.my_user.first_name = 'First'
        self.my_user.last_name = 'Second'
        self.my_user.save()
        self.assertEquals(self.my_user.full_name, 'First Second')

    def test_profile_no_full_name(self):
        self.assertEquals(self.my_user.full_name, "Bartosz")


class ProfileCreationFormTest(TestCase):
    def setUp(self):
        self.form = ProfileCreationForm(data={
            'username': 'Bartosz',
            'password1': 'Tester123',
            'password2': 'Tester123',
        })

    def test_init(self):
        self.form.save()
        profile = Profile.objects.filter(username='Bartosz')
        self.assertTrue(profile.exists())

    def test_is_valid(self):
        self.assertTrue(self.form.is_valid())

    def test_clean_email(self):
        Profile.objects.create_user(
            username='Bartosz',
            password='TEST',
            email='tester@example.pl'
        )
        self.form.email = 'tester@example.pl'
        self.assertFalse(self.form.is_valid())


class ProfileViewTest(TestCase):

    def setUp(self):
        url = reverse('profiles:signup')
        self.get_response = self.client.get(url)

    def test_status_response(self):
        self.assertEquals(self.get_response.status_code, 200)

    def test_profile_url_revolves_profile_view(self):
        view = resolve('/profile/signup/')
        self.assertEquals(view.func.view_class, MyProfileCreationView)

    def test_create_profile(self):
        url = reverse('profiles:signup')
        profile_data = {
            'username': 'Bartosz',
            'email': 'bartosz@example.pl',
            'password1': 'Tester123',
            'password2': 'Tester123',
        }
        response = self.client.post(url, profile_data)
        profile = Profile.objects.filter(username='Bartosz').first()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(profile)
        self.assertEqual(profile.image, 'default.png')



