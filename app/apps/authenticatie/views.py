import logging
from urllib import parse

import requests
from apps.authenticatie.forms import (
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerBulkImportForm,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

Gebruiker = get_user_model()

logger = logging.getLogger(__name__)


def provider_logout(request):
    logout_url = settings.OIDC_OP_LOGOUT_ENDPOINT
    oidc_id_token = request.session.get("oidc_id_token", None)
    redirect_url = request.build_absolute_uri(
        location=request.GET.get("next", settings.LOGOUT_REDIRECT_URL)
    )
    if oidc_id_token:
        logout_url = (
            settings.OIDC_OP_LOGOUT_ENDPOINT
            + "?"
            + parse.urlencode(
                {
                    "id_token_hint": oidc_id_token,
                    "post_logout_redirect_uri": redirect_url,
                }
            )
        )
    logout_response = requests.get(logout_url)
    if logout_response.status_code != 200:
        logger.error(
            f"provider_logout: status code: {logout_response.status_code}, logout_url: {logout_url}"
        )
    return redirect_url


@method_decorator(
    permission_required("authorisatie.gebruiker_bekijken"), name="dispatch"
)
class GebruikerView(View):
    model = Gebruiker
    success_url = reverse_lazy("gebruiker_lijst")


@method_decorator(
    permission_required("authorisatie.gebruiker_lijst_bekijken"), name="dispatch"
)
class GebruikerLijstView(GebruikerView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.object_list
        context["geauthoriseerde_gebruikers"] = object_list.filter(groups__isnull=False)
        context["ongeauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=True
        )
        return context


class GebruikerAanmakenAanpassenView(GebruikerView):
    def form_valid(self, form):
        if not hasattr(form.instance, "profiel"):
            form.instance.save()
        if form.cleaned_data.get("context"):
            form.instance.profiel.context = form.cleaned_data.get("context")
        else:
            form.instance.profiel.context = None
        form.instance.profiel.save()
        form.instance.groups.clear()
        if form.cleaned_data.get("group"):
            form.instance.groups.add(form.cleaned_data.get("group"))

        return super().form_valid(form)


@method_decorator(
    permission_required("authorisatie.gebruiker_aanpassen"), name="dispatch"
)
class GebruikerAanpassenView(GebruikerAanmakenAanpassenView, UpdateView):
    form_class = GebruikerAanpassenForm
    template_name = "authenticatie/gebruiker_aanpassen.html"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial


@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken"), name="dispatch"
)
class GebruikerAanmakenView(GebruikerAanmakenAanpassenView, CreateView):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm


def gebruiker_bulk_import(request):
    form = GebruikerBulkImportForm()
    aangemaakte_gebruikers = None
    if request.POST:
        form = GebruikerBulkImportForm(request.POST)
        if form.is_valid() and request.POST.get("aanmaken"):
            aangemaakte_gebruikers = form.submit()
            form = None
    return render(
        request,
        "authenticatie/gebruiker_bulk_import.html",
        {
            "form": form,
            "aangemaakte_gebruikers": aangemaakte_gebruikers,
        },
    )
