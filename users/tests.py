from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import LoginForm, RegistrationForm


class UserInterfaceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='strongpass123',
        )

    def test_registration_form_uses_russian_labels_and_help(self):
        form = RegistrationForm()

        self.assertEqual(form.fields['username'].label, 'Имя пользователя')
        self.assertEqual(form.fields['password1'].label, 'Пароль')
        self.assertEqual(form.fields['password2'].label, 'Подтверждение пароля')
        self.assertIn('не менее 8 символов', form.fields['password1'].help_text)

    def test_login_form_uses_russian_labels(self):
        form = LoginForm()

        self.assertEqual(form.fields['username'].label, 'Имя пользователя')
        self.assertEqual(form.fields['password'].label, 'Пароль')

    def test_login_and_register_pages_render_without_english_default_labels(self):
        login_response = self.client.get(reverse('users:login'))
        register_response = self.client.get(reverse('users:register'))

        self.assertContains(login_response, 'Имя пользователя')
        self.assertContains(register_response, 'Подтверждение пароля')
        self.assertNotContains(login_response, 'Username:')
        self.assertNotContains(register_response, 'Password confirmation:')

    def test_profile_pages_render_for_authenticated_user(self):
        self.client.login(username='tester', password='strongpass123')

        profile_response = self.client.get(reverse('users:profile'))
        edit_response = self.client.get(reverse('users:profile_edit'))

        self.assertContains(profile_response, 'Мой профиль')
        self.assertContains(edit_response, 'Редактирование профиля')
        self.assertContains(edit_response, 'Имя пользователя')
