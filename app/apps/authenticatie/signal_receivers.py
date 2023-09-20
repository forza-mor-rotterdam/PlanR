from apps.authenticatie.models import Profiel
from apps.context.models import Context
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not hasattr(instance, "profiel"):
        standaard_context, aangemaakt = Context.objects.get_or_create(naam="Standaard")
        Profiel.objects.create(gebruiker=instance, context=standaard_context)
    if hasattr(instance, "profiel") and not instance.profiel.context:
        standaard_context, aangemaakt = Context.objects.get_or_create(naam="Standaard")
        instance.profiel.context = standaard_context
        instance.profiel.save()
