import json

from apps.context.forms import ContextAanmakenForm, ContextAanpassenForm
from apps.context.models import Context
from apps.services.meldingen import MeldingenService
from apps.services.onderwerpen import OnderwerpenService
from apps.services.taakr import TaakRService
from django.contrib.auth.decorators import permission_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(permission_required("authorisatie.context_bekijken"), name="dispatch")
class ContextView(View):
    model = Context
    success_url = reverse_lazy("context_lijst")


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
        urgentie = (
            form.cleaned_data.get("urgentie")
            if form.cleaned_data.get("urgentie")
            else '{"urgentie_gte": 0.0}'
        )
        standaard_filters.update(json.loads(urgentie))
        form.instance.standaard_filters = standaard_filters
        return super().form_valid(form)


@method_decorator(
    permission_required("authorisatie.context_aanpassen"), name="dispatch"
)
class ContextAanpassenView(ContextAanmakenAanpassenView, UpdateView):
    form_class = ContextAanpassenForm

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["taaktypes"] = TaakRService(request=self.request).get_taaktypes(
            use_cache=False
        )
        kwargs["onderwerp_alias_list"] = (
            MeldingenService(request=self.request)
            .onderwerp_alias_list()
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


@method_decorator(permission_required("authorisatie.context_aanmaken"), name="dispatch")
class ContextAanmakenView(ContextAanmakenAanpassenView, CreateView):
    form_class = ContextAanmakenForm


@method_decorator(
    permission_required("authorisatie.context_verwijderen"), name="dispatch"
)
class ContextVerwijderenView(ContextView, DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
