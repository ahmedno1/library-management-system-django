from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Profile


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Jane Doe"}),
        label="Full name",
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))
    phone_number = forms.CharField(
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "+1 555 123 4567"}),
        label="Phone number",
    )
    photo = forms.ImageField(required=False, label="Profile photo")

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(["full_name", "username", "email", "phone_number", "photo", "password1", "password2"])

        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs.setdefault("class", "form-control")

        self.fields["photo"].widget.attrs.setdefault("class", "form-control")
        self.fields["username"].widget.attrs.setdefault("placeholder", "Choose a username")
        self.fields["password1"].widget.attrs.setdefault("placeholder", "Create a password")
        self.fields["password2"].widget.attrs.setdefault("placeholder", "Confirm password")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email

        UserModel = get_user_model()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            return username

        UserModel = get_user_model()
        if UserModel.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1 and len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password1

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, _created = Profile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data["full_name"]
            profile.phone_number = self.cleaned_data.get("phone_number", "").strip()
            photo = self.cleaned_data.get("photo")
            if photo:
                profile.photo = photo
            profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = get_user_model()
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "phone_number", "photo"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
