from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django import forms

from core.forms import BootstrapFormMixin

from .models import User


class SignupForm(BootstrapFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
            "bio",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not settings.ALLOW_ADMIN_SIGNUP:
            self.fields["role"].choices = [(User.ROLE_MEMBER, "Member")]
            self.fields["role"].initial = User.ROLE_MEMBER

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Username or email")

    def clean(self):
        username = self.cleaned_data.get("username", "")
        if "@" in username:
            try:
                user = User.objects.get(email__iexact=username)
                self.cleaned_data["username"] = user.username
            except User.DoesNotExist:
                pass
        return super().clean()


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "bio")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        queryset = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("A user with this email already exists.")
        return email
