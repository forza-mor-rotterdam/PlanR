from apps.context.models import Context
from django.contrib import admin


class ContextAdmin(admin.ModelAdmin):
    ...


admin.site.register(Context, ContextAdmin)
