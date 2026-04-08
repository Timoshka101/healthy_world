from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import Profile


USERNAME_HELP = 'До 150 символов. Можно использовать буквы, цифры и знаки @ . + - _.'
PASSWORD_HELP = mark_safe(
    '<ul class="app-help-list">'
    '<li>Пароль не должен быть слишком похож на ваши личные данные.</li>'
    '<li>Пароль должен содержать не менее 8 символов.</li>'
    '<li>Не используйте слишком простой или распространённый пароль.</li>'
    '<li>Пароль не может состоять только из цифр.</li>'
    '</ul>'
)


class StyledFieldsMixin:
    field_class_map = {
        forms.TextInput: 'form-control app-auth-control',
        forms.PasswordInput: 'form-control app-auth-control',
        forms.EmailInput: 'form-control app-auth-control',
        forms.NumberInput: 'form-control app-auth-control',
        forms.URLInput: 'form-control app-auth-control',
        forms.DateInput: 'form-control app-auth-control',
        forms.Textarea: 'form-control app-auth-control app-auth-textarea',
        forms.Select: 'form-select app-auth-control',
        forms.ClearableFileInput: 'form-control app-auth-control app-auth-file',
        forms.FileInput: 'form-control app-auth-control app-auth-file',
    }

    def apply_field_styles(self):
        for field in self.fields.values():
            for widget_type, css_class in self.field_class_map.items():
                if isinstance(field.widget, widget_type):
                    existing = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f'{existing} {css_class}'.strip()
                    break

class RegistrationForm(StyledFieldsMixin, UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        help_text=USERNAME_HELP,
        widget=forms.TextInput(attrs={'placeholder': 'Придумайте логин'})
    )
    password1 = forms.CharField(
        label='Пароль',
        help_text=PASSWORD_HELP,
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        help_text='Введите тот же пароль ещё раз, чтобы подтвердить его.',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ('username',) # Только логин

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_field_styles()

class LoginForm(AuthenticationForm, StyledFieldsMixin):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'placeholder': 'Введите логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    error_messages = {
        'invalid_login': 'Не удалось войти. Проверьте имя пользователя и пароль.',
        'inactive': 'Этот аккаунт отключён.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_field_styles()

class ProfileUpdateForm(forms.ModelForm, StyledFieldsMixin):
    bio = forms.CharField(
        label='О себе',
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Коротко расскажите о себе или о своих целях в питании'}),
        required=False
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    remove_avatar = forms.BooleanField(label='Удалить текущую аватарку', required=False)

    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_field_styles()

    def save(self, commit=True):
        profile = super().save(commit=False)

        if self.cleaned_data.get('remove_avatar') and profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None

        if commit:
            profile.save()

        return profile

class UserUpdateForm(forms.ModelForm, StyledFieldsMixin):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = USERNAME_HELP
        self.fields['username'].widget.attrs.update({'placeholder': 'Измените логин при необходимости'})
        self.apply_field_styles()
