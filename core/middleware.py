from core.current_user import clear_current_user, set_current_user


class CurrentUserMiddleware:
    """
    Stores the authenticated user in thread-local storage so model signals can
    create activity records without tightly coupling to the request layer.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        set_current_user(user if user and user.is_authenticated else None)
        try:
            response = self.get_response(request)
        finally:
            clear_current_user()
        return response
