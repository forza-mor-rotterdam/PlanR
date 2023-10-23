from django.contrib.auth.decorators import permission_required
from django.shortcuts import render


@permission_required("authorisatie.beheer_bekijken")
def beheer(request):
    return render(
        request,
        "beheer.html",
        {},
    )
