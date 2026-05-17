from django.urls import path

from .views import (
    DashboardAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProjectCreateAPIView,
    ProjectDeleteAPIView,
    ProjectListAPIView,
    ProjectUpdateAPIView,
    SignupAPIView,
    TaskCreateAPIView,
    TaskDeleteAPIView,
    TaskListAPIView,
    TaskUpdateAPIView,
)

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="api-signup"),
    path("login/", LoginAPIView.as_view(), name="api-login"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("projects/", ProjectListAPIView.as_view(), name="api-projects"),
    path("projects/create/", ProjectCreateAPIView.as_view(), name="api-project-create"),
    path("projects/<int:pk>/update/", ProjectUpdateAPIView.as_view(), name="api-project-update"),
    path("projects/<int:pk>/delete/", ProjectDeleteAPIView.as_view(), name="api-project-delete"),
    path("tasks/", TaskListAPIView.as_view(), name="api-tasks"),
    path("tasks/create/", TaskCreateAPIView.as_view(), name="api-task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateAPIView.as_view(), name="api-task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteAPIView.as_view(), name="api-task-delete"),
    path("dashboard/", DashboardAPIView.as_view(), name="api-dashboard"),
]
