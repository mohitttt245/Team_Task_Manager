from django.urls import path

from .views import TaskCreateView, TaskDeleteView, TaskListView, TaskStatusUpdateView, TaskUpdateView

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="list"),
    path("create/", TaskCreateView.as_view(), name="create"),
    path("<int:pk>/update/", TaskUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(), name="delete"),
    path("<int:pk>/status/", TaskStatusUpdateView.as_view(), name="status-update"),
]
