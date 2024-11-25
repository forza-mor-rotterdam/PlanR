from apps.release_notes.forms import (
    BijlageFormSet,
    ReleaseNoteAanmakenForm,
    ReleaseNoteAanpassenForm,
)
from apps.release_notes.tasks import task_aanmaken_afbeelding_versies
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Case, Exists, OuterRef, Q, Value, When
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django_celery_beat.models import ClockedSchedule, PeriodicTask

from .models import Bijlage, ReleaseNote


class ReleaseNoteView(View):
    model = ReleaseNote
    success_url = reverse_lazy("release_note_lijst")


class ReleaseNoteListView(PermissionRequiredMixin, ReleaseNoteView, ListView):
    template_name = "beheer/release_note_list.html"
    context_object_name = "release_notes"
    permission_required = "authorisatie.release_note_lijst_bekijken"
    # form_class = ReleaseNoteSearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(titel__icontains=search) | Q(tekst__icontains=search)
            )
        queryset = queryset.order_by("-publicatie_datum", "-aangemaakt_op")

        return queryset

    def profiel_notificatie_queryset(self):
        queryset = super().get_queryset()

        queryset = (
            queryset.filter(publicatie_datum__lt=timezone.now())
            .filter(
                Q(einde_publicatie_datum__isnull=True)
                | (
                    Q(einde_publicatie_datum__isnull=False)
                    & Q(einde_publicatie_datum__gt=timezone.now())
                )
            )
            .filter(bericht_type=ReleaseNote.BerichtTypeOpties.NOTIFICATIE)
            .order_by("-publicatie_datum")
        )

        return queryset


class ReleaseNoteDetailView(LoginRequiredMixin, ReleaseNoteView, DetailView):
    template_name = "public/release_note_detail.html"
    context_object_name = "release_note"

    def get(self, request, *args, **kwargs):
        release_note = get_object_or_404(ReleaseNote, pk=kwargs["pk"])
        release_note.bekeken_door_gebruikers.add(request.user)
        origine = request.session.pop("origine", "release_note_lijst_public")
        context = {"release_note": release_note, "origine": origine}
        return render(request, self.template_name, context)


class NotificatieLijstViewPublic(ListView):
    template_name = "public/notificaties/notificatie_lijst.html"
    queryset = ReleaseNote.objects.filter(
        bericht_type=ReleaseNote.BerichtTypeOpties.NOTIFICATIE
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = (
            self.get_queryset()
            .filter(publicatie_datum__lt=timezone.now())
            .filter(
                Q(einde_publicatie_datum__isnull=True)
                | (
                    Q(einde_publicatie_datum__isnull=False)
                    & Q(einde_publicatie_datum__gt=timezone.now())
                )
            )
            .exclude(bekeken_door_gebruikers=self.request.user)
            .order_by("-publicatie_datum")
        )
        for notificatie_type, _ in ReleaseNote.NotificatieTypeOpties.choices:
            context.update(
                {notificatie_type: qs.filter(notificatie_type=notificatie_type)}
            )
        return context


class ProfielNotificatieLijstViewPublic(ReleaseNoteListView):
    template_name = "public/notificaties/profiel_notificatie_lijst.html"
    queryset = ReleaseNote.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = (
            queryset.filter(publicatie_datum__lt=timezone.now())
            .filter(
                Q(einde_publicatie_datum__isnull=True)
                | (
                    Q(einde_publicatie_datum__isnull=False)
                    & Q(einde_publicatie_datum__gt=timezone.now())
                )
            )
            .filter(bericht_type=ReleaseNote.BerichtTypeOpties.NOTIFICATIE)
            .order_by("-publicatie_datum")
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.profiel_notificatie_queryset()
        page_size = 5
        page = 0
        try:
            page = int(self.request.GET.get("p"))
        except Exception:
            ...
        queryset[page * page_size : (page + 1) * page_size]

        context.update(
            {
                "paginering": {
                    "object_list": queryset[page * page_size : (page + 1) * page_size],
                    "p": page,
                    "volgende": page + 1
                    if queryset[(page + 1) * page_size : (page + 2) * page_size]
                    else None,
                    "vorige": page - 1 if page != 0 else None,
                },
                "ongezien_aantal": queryset.exclude(
                    bekeken_door_gebruikers=self.request.user
                ),
            }
        )
        return context


class NotificatieVerwijderViewPublic(LoginRequiredMixin, DetailView):
    template_name = "public/notificaties/notificatie_verwijderd.html"
    queryset = ReleaseNote.objects.filter(
        bericht_type=ReleaseNote.BerichtTypeOpties.NOTIFICATIE
    )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.bekeken_door_gebruikers.add(self.request.user)
        return obj


class ReleaseNoteListViewPublic(LoginRequiredMixin, ReleaseNoteView, ListView):
    template_name = "public/release_note_list.html"
    context_object_name = "release_notes"
    # form_class = ReleaseNoteSearchForm

    def get_queryset(self):
        five_weeks_ago = timezone.now() - timezone.timedelta(weeks=5)
        queryset = (
            super()
            .get_queryset()
            .annotate(
                is_unwatched=Case(
                    When(
                        Exists(
                            ReleaseNote.bekeken_door_gebruikers.through.objects.filter(
                                releasenote_id=OuterRef("pk"),
                                gebruiker_id=self.request.user.id,
                            )
                        ),
                        then=Value(False),
                    ),
                    default=Value(True),
                    output_field=BooleanField(),
                )
            )
            .filter(
                publicatie_datum__lte=timezone.now(),
                publicatie_datum__gte=five_weeks_ago,
            )
            .order_by("-publicatie_datum", "-aangemaakt_op")
        ).filter(bericht_type=ReleaseNote.BerichtTypeOpties.RELEASE_NOTE)

        return queryset

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        request.session["origine"] = "release_note_lijst_public"
        return response


class ReleaseNoteAanmakenView(PermissionRequiredMixin, ReleaseNoteView, CreateView):
    form_class = ReleaseNoteAanmakenForm
    template_name = "beheer/release_note_aanmaken.html"
    permission_required = "authorisatie.release_note_aanmaken"

    def form_valid(self, form):
        response = super().form_valid(form)

        bijlagen = self.request.FILES.getlist("bijlagen", [])

        for file in bijlagen:
            bijlage = Bijlage(
                content_type=ContentType.objects.get_for_model(self.object),
                object_id=self.object.id,
                bestand=file,
                mimetype=file.content_type,
                is_afbeelding=False,
            )
            bijlage.save()

            task_aanmaken_afbeelding_versies.delay(bijlage.pk)
        messages.success(
            request=self.request, message=f"De {self.object.bericht_type} is aangemaakt"
        )

        if self.object.bericht_type == ReleaseNote.BerichtTypeOpties.NOTIFICATIE:
            clocked_schedule = ClockedSchedule.objects.create(
                clocked_time=self.object.publicatie_datum
            )
            PeriodicTask.objects.create(
                clocked=clocked_schedule,
                name=f"clocked_periodic_task_notificatie_{self.object.id}",
                task="apps.release_notes.tasks.task_activeer_notificatie",
                one_off=True,
                args=[self.object.id],
            )

        return response


class ReleaseNoteAanpassenView(PermissionRequiredMixin, ReleaseNoteView, UpdateView):
    form_class = ReleaseNoteAanpassenForm

    template_name = "beheer/release_note_aanpassen.html"
    permission_required = "authorisatie.release_note_aanpassen"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = BijlageFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object,
                prefix="bijlage",
            )
        else:
            context["formset"] = BijlageFormSet(instance=self.object, prefix="bijlage")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            for bijlage_form in formset.forms:
                if bijlage_form.is_valid():
                    bijlage = bijlage_form.save(commit=False)
                    bijlage.content_object = self.object
                    bijlage.save()
                    task_aanmaken_afbeelding_versies.delay(bijlage.pk)
            formset.save()

            bijlagen = self.request.FILES.getlist("bijlagen", [])

            for file in bijlagen:
                bijlage = Bijlage(
                    content_type=ContentType.objects.get_for_model(self.object),
                    object_id=self.object.id,
                    bestand=file,
                    mimetype=file.content_type,
                    is_afbeelding=False,
                )
                bijlage.save()

                task_aanmaken_afbeelding_versies.delay(bijlage.pk)
            messages.success(
                request=self.request,
                message=f"De {self.object.bericht_type} is aangepast",
            )

            if self.object.bericht_type == ReleaseNote.BerichtTypeOpties.NOTIFICATIE:
                PeriodicTask.objects.filter(
                    name=f"clocked_periodic_task_notificatie_{self.object.id}"
                ).delete()
                clocked_schedule = ClockedSchedule.objects.create(
                    clocked_time=self.object.publicatie_datum
                )
                PeriodicTask.objects.create(
                    clocked=clocked_schedule,
                    name=f"clocked_periodic_task_notificatie_{self.object.id}",
                    task="apps.release_notes.tasks.task_activeer_notificatie",
                    one_off=True,
                    args=[self.object.id],
                )

            return super().form_valid(form)
        else:
            messages.error(
                request=self.request,
                message="Er ging iets mis met het aanpassen van het bericht",
            )
            return self.render_to_response(
                self.get_context_data(form=form, formset=formset)
            )


class ReleaseNoteVerwijderenView(PermissionRequiredMixin, ReleaseNoteView, DeleteView):
    permission_required = "authorisatie.release_note_verwijderen"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
