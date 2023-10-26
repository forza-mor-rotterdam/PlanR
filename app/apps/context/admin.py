from apps.context.models import Context
from django.contrib import admin
from django.contrib.admin import AdminSite

AdminSite.site_title = "PlanR Admin"
AdminSite.site_header = "PlanR Admin"
AdminSite.index_title = "PlanR Admin"


class ContextAdmin(admin.ModelAdmin):
    ...


admin.site.register(Context, ContextAdmin)
