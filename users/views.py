from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import RegistrationForm, LoginForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('games_home') # Перенаправить на игры после регистрации
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('games_home') # Перенаправить на игры после входа
    else:
        form = LoginForm(request)
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('games_home') # Перенаправить на игры после выхода

@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=profile)
    return render(
        request,
        'users/profile.html',
        {'user_form': user_form, 'profile_form': profile_form, 'profile': profile},
    )

@login_required
def profile_update(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:profile') # Перенаправить на страницу профиля
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    return render(
        request,
        'users/profile_edit.html',
        {'user_form': user_form, 'profile_form': profile_form, 'profile': profile},
    )

def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    return render(request, 'users/user_detail.html', {'profile': profile, 'user_obj': user})
