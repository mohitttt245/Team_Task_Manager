from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.mixins import AdminRequiredMixin, MemberRequiredMixin, get_dashboard_url

from .services import get_admin_dashboard_data, get_member_dashboard_data


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect(get_dashboard_url(request.user))


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_admin_dashboard_data())
        return context


class MemberDashboardView(MemberRequiredMixin, TemplateView):
    template_name = "dashboard/member_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_member_dashboard_data(self.request.user))
        return context
