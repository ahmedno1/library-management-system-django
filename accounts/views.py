from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ProfileForm, RegisterForm, UserUpdateForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("library:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. You are now logged in.")
            login(request, user)
            return redirect("library:home")
        messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("library:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("library:home")
        messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("library:home")


@login_required
def profile_view(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": profile})


@login_required
def profile_edit_view(request):
    profile, _created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
        messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/profile_edit.html", context)
