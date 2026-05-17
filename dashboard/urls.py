from django.urls import path

from .views import AdminDashboardView, DashboardHomeView, MemberDashboardView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin"),
    path("dashboard/member/", MemberDashboardView.as_view(), name="member"),
]
