from django.conf import settings
from django.utils.timezone import now


def app_context(request):
    return {
        "APP_NAME": "Team Task Manager",
        "CURRENT_YEAR": now().year,
        "ALLOW_ADMIN_SIGNUP": settings.ALLOW_ADMIN_SIGNUP,
    }
