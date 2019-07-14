from django.test import TestCase, override_settings
from django.urls import reverse
from django.core import mail

from my_wallet.portfolio.models import Portfolio
from my_wallet.profiles.models import Profile
from my_wallet.profiles.forms import ProfileCreationForm, ProfileUpdateForm


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(username='Tester', password='Tester123')

    def test_profile_creation_get(self):
        url = reverse('profiles:signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIsInstance(form, ProfileCreationForm)

    def test_profile_creation_post_valid(self):
        url = reverse('profiles:signup')
        data = {
            'username': 'Bartek',
            'password1': 'Tester123',
            'password2': 'Tester123',
            'address': 'Piękna'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_profile_creation_post_invalid(self):
        url = reverse('profiles:signup')
        data = {
            'username': 'Bartek',
            'password1': 'Tester123',
            'password2': 'Tester',
            'address': 'Piękna'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_profile_view_no_portfolios(self):
        self.client.force_login(user=self.user)
        url = reverse('profiles:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        msg = 'Nie posiadasz jeszcze żadnego portfela.'
        self.assertContains(response, msg)

    def test_profile_view_with_portfolios(self):
        self.client.force_login(user=self.user)
        portfolio = Portfolio.objects.create(
            name='Test Portfolio', profile=self.user,
            cash=10000, beginning_cash=10000)
        url = reverse('profiles:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected = [portfolio, ]
        self.assertListEqual(list(response.context['portfolios']), expected)

    def test_edit_profile(self):
        self.client.force_login(user=self.user)
        url = reverse('profiles:edit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ProfileUpdateForm)

    def test_edit_profile_post(self):
        self.client.force_login(user=self.user)
        url = reverse('profiles:edit')
        data = {
            'first_name': 'Bartek'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        actual = Profile.objects.first().first_name
        self.assertEqual(actual, 'Bartek')

    def test_password_change_no_login(self):
        url = reverse('profiles:password_change')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_password_change(self):
        self.client.force_login(user=self.user)
        url = reverse('profiles:password_change')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'old_password': 'Tester123',
            'new_password1': 'MyNewPassword468',
            'new_password2': 'MyNewPassword468'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_contact(self):
        url = reverse('profiles:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(EMAIL_HOST_USER='test_mail')
    def test_contact_post_valid(self):
        url = reverse('profiles:contact')
        data = {
            'subject': 'To jest tytuł',
            'content': 'To jest treść',
            'email': 'bartosz@wp.pl'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), ['test_mail@gmail.com'])

    def test_contact_post_invalid(self):
        url = reverse('profiles:contact')
        data = {
            'subject': 'To jest tytuł',
            'content': 'To jest treść',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'To pole jest wymagane.')



