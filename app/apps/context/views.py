from apps.context.forms import ContextAanmakenForm, ContextAanpassenForm
from apps.context.models import Context
from apps.main.services import MORCoreService, OnderwerpenService, TaakRService
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("authorisatie.context_bekijken"), name="dispatch")
class ContextView(View):
    model = Context
    success_url = reverse_lazy("context_lijst")


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_lijst_bekijken"), name="dispatch"
)
class ContextLijstView(ContextView, ListView):
    ...


class ContextAanmakenAanpassenView(ContextView):
    def form_valid(self, form):
        form.instance.filters = {"fields": form.cleaned_data.get("filters")}
        form.instance.kolommen = {"sorted": form.cleaned_data.get("kolommen")}
        standaard_filters = {
            "pre_onderwerp": form.cleaned_data.get("standaard_filters", []),
        }
        form.instance.standaard_filters = standaard_filters
        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_aanpassen"), name="dispatch"
)
class ContextAanpassenView(
    SuccessMessageMixin, ContextAanmakenAanpassenView, UpdateView
):
    form_class = ContextAanpassenForm
    success_message = "De rol '%(naam)s' is aangepast"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        taakr_service = TaakRService()
        taakr_service.get_afdelingen(force_cache=True)
        kwargs["taaktypes"] = taakr_service.get_taaktypes(force_cache=True)
        kwargs["onderwerp_alias_list"] = (
            MORCoreService(request=self.request)
            .onderwerp_alias_list(force_cache=True)
            .get("results", [])
        )
        kwargs["onderwerpen_service"] = OnderwerpenService(request=self.request)
        return kwargs

    def get_initial(self):
        initial = self.initial.copy()
        obj = self.get_object()
        initial["filters"] = obj.filters.get("fields", [])
        initial["kolommen"] = obj.kolommen.get("sorted", [])
        initial["standaard_filters"] = obj.standaard_filters.get("pre_onderwerp", [])
        return initial


@method_decorator(login_required, name="dispatch")
@method_decorator(permission_required("authorisatie.context_aanmaken"), name="dispatch")
class ContextAanmakenView(
    SuccessMessageMixin, ContextAanmakenAanpassenView, CreateView
):
    form_class = ContextAanmakenForm
    success_message = "De rol '%(naam)s' is aangemaakt"

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["taaktypes"] = TaakRService(request=self.request).get_taaktypes(
            force_cache=True
        )
        kwargs["onderwerp_alias_list"] = (
            MORCoreService(request=self.request)
            .onderwerp_alias_list(force_cache=True)
            .get("results", [])
        )
        kwargs["onderwerpen_service"] = OnderwerpenService(request=self.request)
        return kwargs


@method_decorator(login_required, name="dispatch")
@method_decorator(
    permission_required("authorisatie.context_verwijderen"), name="dispatch"
)
class ContextVerwijderenView(ContextView, DeleteView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if not object.profielen_voor_context.all():
            response = self.delete(request, *args, **kwargs)
            messages.success(self.request, f"De rol '{object.naam}' is verwijderd")
            return response
        return HttpResponse("Verwijderen is niet mogelijk")
