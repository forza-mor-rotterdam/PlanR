import logging

from apps.context.constanten import FilterManager
from apps.context.utils import get_gebruiker_context
from apps.main.forms import FilterForm
from apps.main.messages import MELDING_LIJST_OPHALEN_ERROR
from apps.main.services import MORCoreService
from apps.main.utils import (
    get_actieve_filters,
    get_ui_instellingen,
    get_valide_kolom_classes,
    set_actieve_filters,
    set_ui_instellingen,
    update_qd_met_standaard_meldingen_filter_qd,
)
from deepdiff import DeepDiff
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, QueryDict
from django.shortcuts import render

logger = logging.getLogger(__name__)


@login_required
@permission_required("authorisatie.melding_lijst_bekijken", raise_exception=True)
def melding_lijst(request):
    # Handle AJAX filter count request
    if request.GET.get('action') == 'filter_count':
        return _get_filter_count(request)
    
    mor_core_service = MORCoreService()
    gebruiker = request.user
    gebruiker_context = get_gebruiker_context(gebruiker)

    standaard_waardes = {
        "limit": "25",
        "foldout_states": "[]",
        "offset": "0",
    }
    standaard_waardes.update(get_ui_instellingen(gebruiker))
    actieve_filters = get_actieve_filters(gebruiker)

    qs = QueryDict("", mutable=True)
    qs.update(request.GET)

    # remove unused GET vars
    allowed_querystring_params = list(actieve_filters.keys()) + [
        "ordering",
        "q",
        "offset",
    ]
    qs_keys = list(qs.keys())
    [qs.pop(k, None) for k in qs_keys if k not in allowed_querystring_params]

    qs.update(request.POST)

    if qs:
        nieuwe_actieve_filters = {
            k: qs.getlist(k, []) for k, v in actieve_filters.items()
        }
        standaard_waardes.update(
            set_ui_instellingen(
                gebruiker,
                qs.get("ordering", standaard_waardes["ordering"]),
                qs.get("search_with_profiel_context"),
            )
        )
        standaard_waardes["foldout_states"] = qs.get("foldout_states")

        # reset pagination offset if meldingen count most likely will change by changing filters
        if DeepDiff(actieve_filters, nieuwe_actieve_filters) or qs.get(
            "q", ""
        ) != request.session.get("q", ""):
            request.session["offset"] = "0"
        else:
            request.session["offset"] = qs.get("offset", "0")

        if qs.get("q"):
            request.session["q"] = qs.get("q", "")
        elif request.session.get("q"):
            del request.session["q"]

        actieve_filters = set_actieve_filters(gebruiker, nieuwe_actieve_filters)

    standaard_waardes["offset"] = request.session.get("offset", "0")

    form_qs = QueryDict("", mutable=True)
    if request.session.get("q"):
        form_qs.update(
            {
                "q": request.session.get("q"),
            }
        )
    form_qs.update(standaard_waardes)

    for k, v in actieve_filters.items():
        if v:
            form_qs.setlist(k, v)

    meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
        form_qs, gebruiker_context
    )
    meldingen_data = mor_core_service.get_melding_lijst(
        query_string=FilterManager(
            gebruiker_context=gebruiker_context
        ).get_query_string(meldingen_filter_query_dict)
    )
    if (
        len(meldingen_data.get("results", [])) == 0
        and meldingen_filter_query_dict.get("offset") != "0"
    ):
        # reset pagination to first page if meldingen result is empty and the offset is not 0
        meldingen_filter_query_dict["offset"] = "0"
        form_qs["offset"] = "0"
        request.session["offset"] = "0"
        meldingen_data = mor_core_service.get_melding_lijst(
            query_string=FilterManager(
                gebruiker_context=gebruiker_context
            ).get_query_string(meldingen_filter_query_dict)
        )
    if isinstance(meldingen_data, dict) and meldingen_data.get("error"):
        messages.error(request=request, message=MELDING_LIJST_OPHALEN_ERROR)

    request.session["pagina_melding_ids"] = [
        r.get("uuid") for r in meldingen_data.get("results", [])
    ]
    request.session["melding_count"] = meldingen_data.get("count", 0)

    form = FilterForm(
        form_qs,
        gebruiker=gebruiker,
        meldingen_data=meldingen_data,
    )

    form.is_valid()
    if form.errors:
        logger.warning(form.errors)

    return render(
        request,
        "melding/melding_lijst.html",
        {
            "data": meldingen_data,
            "form": form,
            "kolommen": get_valide_kolom_classes(gebruiker_context),
        },
    )


def _get_filter_count(request):
    """Return the count of melding matching the current filter selection."""
    try:
        mor_core_service = MORCoreService()
        gebruiker = request.user
        gebruiker_context = get_gebruiker_context(gebruiker)
        
        from apps.main.utils import get_valide_filter_classes
        
        # Get all possible filter field names
        filter_classes = get_valide_filter_classes(gebruiker_context)
        filter_field_names = [cls.key() for cls in filter_classes]
        
        # Build query dict with filter data from the POST request
        form_qs = QueryDict("", mutable=True)
        
        # Include search query if present
        if request.POST.get('q'):
            form_qs['q'] = request.POST.get('q')

        # Mirror regular form behavior for applying profile defaults.
        if request.POST.get('search_with_profiel_context'):
            form_qs['search_with_profiel_context'] = request.POST.get('search_with_profiel_context')
        
        # Add filter values from POST data for all filter fields
        for field_name in filter_field_names:
            values = request.POST.getlist(field_name)
            if values:
                form_qs.setlist(field_name, values)
        
        logger.debug(f"Filter count query: {dict(form_qs)}")
        
        # Build the filter query dict
        meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
            form_qs, gebruiker_context
        )
        
        logger.debug(f"Processed filter query: {dict(meldingen_filter_query_dict)}")
        
        # Get the filtered data with count
        meldingen_data = mor_core_service.get_melding_lijst(
            query_string=FilterManager(
                gebruiker_context=gebruiker_context
            ).get_query_string(meldingen_filter_query_dict)
        )
        
        count = meldingen_data.get("count", 0)
        logger.debug(f"Filter result count: {count}")
        return JsonResponse({"count": count})
    except Exception as e:
        logger.exception(f"Error in _get_filter_count: {e}")
        return JsonResponse({"error": str(e), "count": 0}, status=500)
