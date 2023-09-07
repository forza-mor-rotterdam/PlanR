def get_gebruiker_context(request):
    if (
        hasattr(request, "user")
        and hasattr(request.user, "profiel")
        and hasattr(request.user.profiel, "context")
    ):
        return request.user.profiel.context
    return None
