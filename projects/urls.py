from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectListView,
    ProjectUpdateView,
    TeamManagementUpdateView,
    TeamManagementView,
)

app_name = "projects"

urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ProjectUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ProjectDeleteView.as_view(), name="delete"),
    path("team/", TeamManagementView.as_view(), name="team"),
    path("team/<int:pk>/update/", TeamManagementUpdateView.as_view(), name="team-update"),
]
