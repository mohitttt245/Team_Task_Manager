from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .models import User


def get_dashboard_url(user):
    if user.role == User.ROLE_ADMIN:
        return reverse("dashboard:admin")
    return reverse("dashboard:member")


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles = ()

    def test_func(self):
        return self.request.user.role in self.allowed_roles

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You do not have permission to access that page.")
            return redirect(get_dashboard_url(self.request.user))
        return super().handle_no_permission()


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.ROLE_ADMIN,)


class MemberRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.ROLE_MEMBER,)
