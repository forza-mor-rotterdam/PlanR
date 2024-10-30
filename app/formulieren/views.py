from django.views.generic import TemplateView
from formulieren.forms import BasisForm


def copy_exception(exc, backend=None):
    """
    Create a new TemplateDoesNotExist. Preserve its declared attributes and
    template debug data but discard __traceback__, __context__, and __cause__
    to make this object suitable for keeping around (in a cache, for example).
    """
    backend = backend or exc.backend
    new = exc.__class__(*exc.args, tried=exc.tried, backend=backend, chain=exc.chain)
    if hasattr(exc, "template_debug"):
        new.template_debug = exc.template_debug
    return new


def reraise(exc, backend):
    """
    Reraise TemplateDoesNotExist while maintaining template debug information.
    """
    new = copy_exception(exc, backend)
    raise new from exc


class BasisView(TemplateView):
    template_name = "formulieren/basis.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = BasisForm()

        return context
