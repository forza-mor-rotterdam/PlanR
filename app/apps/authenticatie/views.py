import logging

from apps.authenticatie.forms import (
    GebruikerAanmakenForm,
    GebruikerAanpassenForm,
    GebruikerBulkImportForm,
    GebruikerProfielForm,
)
from apps.instellingen.models import Instelling
from apps.main.services import MORCoreService
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

Gebruiker = get_user_model()

logger = logging.getLogger(__name__)


class SessionTimerView(LoginRequiredMixin, TemplateView):
    template_name = "auth/session_timer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "notificatie": {
                    "id": "session_timer",
                    "notificatie_niveau": "warning",
                    "titel": "Je sessie verloop binnenkort",
                    "korte_beschrijving": "&nbsp;",
                    "link_titel": "Sessie&nbsp;verlengen",
                    "link_url": ".",
                }
            }
        )
        return context


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
        context["geauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=False,
            verwijderd_op__isnull=True,
        )
        context["ongeauthoriseerde_gebruikers"] = object_list.filter(
            groups__isnull=True,
            verwijderd_op__isnull=True,
        )
        context["verwijderde_gebruikers"] = object_list.filter(
            verwijderd_op__isnull=False
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
class GebruikerAanpassenView(
    SuccessMessageMixin, GebruikerAanmakenAanpassenView, UpdateView
):
    form_class = GebruikerAanpassenForm
    template_name = "authenticatie/gebruiker_aanpassen.html"
    success_message = "De gebruiker '%(email)s' is aangepast"

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            email=self.object.email,
        )


@method_decorator(
    permission_required("authorisatie.gebruiker_aanmaken"), name="dispatch"
)
class GebruikerAanmakenView(
    SuccessMessageMixin, GebruikerAanmakenAanpassenView, CreateView
):
    template_name = "authenticatie/gebruiker_aanmaken.html"
    form_class = GebruikerAanmakenForm
    success_message = "De gebruiker '%(email)s' is aangemaakt"


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_verwijderen", raise_exception=True),
    name="dispatch",
)
class GebruikerVerwijderenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = timezone.now()
        object.groups.clear()
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is verwijderd",
        )
        return redirect(reverse("gebruiker_lijst"))


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.gebruiker_terughalen", raise_exception=True),
    name="dispatch",
)
class GebruikerTerughalenView(GebruikerAanmakenAanpassenView, UpdateView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.verwijderd_op = None
        object.save(update_fields=["verwijderd_op"])
        messages.success(
            request,
            f"De gebruiker '{object.email}' is teruggehaald",
        )
        return redirect(reverse("gebruiker_lijst"))


@login_required
@permission_required("authorisatie.gebruiker_aanmaken", raise_exception=True)
def gebruiker_bulk_import(request):
    form = GebruikerBulkImportForm()
    aangemaakte_gebruikers = None
    if request.POST:
        form = GebruikerBulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            request.session["valid_rows"] = form.cleaned_data.get("csv_file", {}).get(
                "valid_rows", []
            )
        if request.session.get("valid_rows") and request.POST.get("aanmaken"):
            aangemaakte_gebruikers = form.submit(request.session.get("valid_rows"))
            messages.success(
                request,
                f"Er zijn {len(aangemaakte_gebruikers)} gebruikers met success aangepast of geïmporteerd",
            )
            del request.session["valid_rows"]
            form = None
    return render(
        request,
        "authenticatie/gebruiker_bulk_import.html",
        {
            "form": form,
            "aangemaakte_gebruikers": aangemaakte_gebruikers,
        },
    )


@method_decorator(login_required, name="dispatch")
class GebruikerProfielView(GebruikerView, UpdateView):
    form_class = GebruikerProfielForm
    template_name = "authenticatie/gebruiker_profiel.html"
    success_url = reverse_lazy("gebruiker_profiel")

    def get_context_data(self, **kwargs):
        instelling = Instelling.actieve_instelling()
        if not instelling or not instelling.email_beheer:
            raise Exception(
                "De beheer_email kan niet worden gevonden, er zijn nog geen instellingen voor aangemaakt"
            )
        context = super().get_context_data(**kwargs)
        context["email_beheer"] = instelling.email_beheer
        return context

    def get_object(self, queryset=None):
        MORCoreService().set_gebruiker(
            gebruiker=self.request.user.serialized_instance(),
        )
        return self.request.user

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        context = obj.profiel.context if hasattr(obj, "profiel") else None
        initial["context"] = context
        initial["group"] = obj.groups.all().first()
        return initial

    def form_valid(self, form):
        messages.success(self.request, "Gebruikersgegevens succesvol opgeslagen.")
        return super().form_valid(form)
