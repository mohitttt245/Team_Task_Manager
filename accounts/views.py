from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, View

from dashboard.models import ActivityLog

from .forms import LoginForm, ProfileForm, SignupForm
from .mixins import LoginRequiredMixin, get_dashboard_url


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(get_dashboard_url(request.user))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        ActivityLog.objects.create(
            actor=user,
            action="signup",
            object_type="user",
            object_id=user.pk,
            message=f"{user.display_name} created an account.",
        )
        messages.success(self.request, "Your account has been created successfully.")
        return redirect(get_dashboard_url(user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allow_admin_signup"] = settings.ALLOW_ADMIN_SIGNUP
        return context


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return get_dashboard_url(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Welcome back.")
        return super().form_valid(form)


class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        response = redirect("accounts:login")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        messages.info(request, "You have been logged out.")
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile was updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["assigned_task_count"] = user.assigned_tasks.count()
        context["project_count"] = user.projects.count()
        return context
