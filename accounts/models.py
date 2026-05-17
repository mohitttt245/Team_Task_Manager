from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "ADMIN"
    ROLE_MEMBER = "MEMBER"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ("username",)

    def clean(self):
        super().clean()
        if not self.email:
            raise ValidationError({"email": "Email is required."})

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_member_role(self):
        return self.role == self.ROLE_MEMBER

    @property
    def display_name(self):
        full_name = self.get_full_name().strip()
        return full_name or self.username

    def __str__(self):
        return f"{self.display_name} ({self.role.title()})"
