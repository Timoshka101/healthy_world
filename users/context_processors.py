from .forms import LoginForm, RegistrationForm


def auth_forms(request):
    if request.user.is_authenticated:
        return {}

    return {
        'login_form': LoginForm(request=request),
        'register_form': RegistrationForm(),
    }
