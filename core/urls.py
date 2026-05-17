from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("", include("accounts.urls")),
    path("projects/", include("projects.urls")),
    path("tasks/", include("tasks.urls")),
    path("api/", include("api.urls")),
]
