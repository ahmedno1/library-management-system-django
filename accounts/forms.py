from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False, label="First name")
    last_name = forms.CharField(required=False, label="Last name")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "photo"]
