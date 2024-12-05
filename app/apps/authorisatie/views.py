from apps.authorisatie.forms import RechtengroepAanmakenForm, RechtengroepAanpassenForm
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView


@method_decorator(
    permission_required("authorisatie.rechtengroep_bekijken"), name="dispatch"
)
class RechtengroepView(View):
    model = Group
    success_url = reverse_lazy("rechtengroep_lijst")


@method_decorator(
    permission_required("authorisatie.rechtengroep_lijst_bekijken"), name="dispatch"
)
class RechtengroepLijstView(RechtengroepView, ListView):
    ...


class RechtengroepAanmakenAanpassenView(RechtengroepView):
    ...


@method_decorator(
    permission_required("authorisatie.rechtengroep_aanpassen"), name="dispatch"
)
class RechtengroepAanpassenView(
    SuccessMessageMixin, RechtengroepAanmakenAanpassenView, UpdateView
):
    form_class = RechtengroepAanpassenForm
    success_message = "De rechtengroep '%(name)s' is aangepast"


@method_decorator(
    permission_required("authorisatie.rechtengroep_aanmaken"), name="dispatch"
)
class RechtengroepAanmakenView(
    SuccessMessageMixin, RechtengroepAanmakenAanpassenView, CreateView
):
    form_class = RechtengroepAanmakenForm
    success_message = "De rechtengroep '%(name)s' is aangemaakt"


@method_decorator(
    permission_required("authorisatie.rechtengroep_verwijderen"), name="dispatch"
)
class RechtengroepVerwijderenView(RechtengroepView, DeleteView):
    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if not object.user_set.all():
            response = self.delete(request, *args, **kwargs)
            messages.success(
                self.request, f"De rechtengroep '{object.name}' is verwijderd"
            )
            return response
        return HttpResponse("Verwijderen is niet mogelijk")
