import ast
import importlib
import json

from apps.main import models
from apps.main.forms import StandaardExterneOmschrijvingAanpassenForm
from apps.main.utils import truncate_tekst
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django_celery_results.admin import TaskResultAdmin
from django_celery_results.models import TaskResult


class MeldingAfhandelredenAdmin(admin.ModelAdmin):
    list_display = [
        "reden",
        "specificatie_opties",
    ]


class StandaardExterneOmschrijvingAdmin(admin.ModelAdmin):
    def korte_tekst(self, obj):
        return truncate_tekst(obj.tekst)

    list_display = [
        "titel",
        "korte_tekst",
        "zichtbaarheid",
        "reden",
        "specificatie_opties",
    ]
    form = StandaardExterneOmschrijvingAanpassenForm

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "titel",
                    "tekst",
                    "zichtbaarheid",
                    "reden",
                    "specificatie_opties",
                ]
            },
        ),
        # ("onderwerpen", {"fields": ["onderwerpen"]})
    )
    search_fields = [
        "titel",
    ]
    ordering = ["titel"]

    korte_tekst.short_description = "Tekst"


admin.site.register(
    models.StandaardExterneOmschrijving, StandaardExterneOmschrijvingAdmin
)
admin.site.register(models.MeldingAfhandelreden, MeldingAfhandelredenAdmin)


def retry_celery_task_admin_action(modeladmin, request, queryset):
    msg = ""
    for task_res in queryset:
        if task_res.status != "FAILURE":
            msg += f'{task_res.task_id} => Skipped. Not in "FAILURE" State<br>'
            continue
        try:
            task_actual_name = task_res.task_name.split(".")[-1]
            module_name = ".".join(task_res.task_name.split(".")[:-1])
            kwargs = json.loads(task_res.task_kwargs)
            if isinstance(kwargs, str):
                kwargs = kwargs.replace("'", '"')
                kwargs = json.loads(kwargs)
                if kwargs:
                    getattr(
                        importlib.import_module(module_name), task_actual_name
                    ).apply_async(kwargs=kwargs, task_id=task_res.task_id)
            if not kwargs:
                args = ast.literal_eval(ast.literal_eval(task_res.task_args))
                getattr(
                    importlib.import_module(module_name), task_actual_name
                ).apply_async(args, task_id=task_res.task_id)
            msg += f"{task_res.task_id} => Successfully sent to queue for retry.<br>"
        except Exception as ex:
            msg += f"{task_res.task_id} => Unable to process. Error: {ex}<br>"
    messages.info(request, mark_safe(msg))


retry_celery_task_admin_action.short_description = "Retry Task"


class CustomTaskResultAdmin(TaskResultAdmin):
    list_filter = (
        "status",
        "date_created",
        "date_done",
        "periodic_task_name",
        "task_name",
    )
    actions = [
        retry_celery_task_admin_action,
    ]


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)
