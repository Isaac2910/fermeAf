"""Vues de l'application « conseils » : demandes d'expertise et fiches techniques."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView, TemplateView,
                                  UpdateView)

from comptes.permissions import ExpertRequisMixin, FermierRequisMixin

from .forms import DemandeConseilForm, FicheTechniqueForm, ReponseForm
from .models import DemandeConseil, FicheTechnique

Statut = DemandeConseil.Statut


# ---------------------------------------------------------------------------
# Côté fermier
# ---------------------------------------------------------------------------
class MesDemandesView(FermierRequisMixin, ListView):
    template_name = "conseils/mes_demandes.html"
    context_object_name = "demandes"
    paginate_by = 12

    def get_queryset(self):
        qs = DemandeConseil.objects.filter(fermier=self.request.user).select_related("expert")
        statut = self.request.GET.get("statut")
        return qs.filter(statut=statut) if statut in Statut.values else qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statuts"] = Statut.choices
        ctx["statut_actif"] = self.request.GET.get("statut", "")
        return ctx


class DemandeCreerView(FermierRequisMixin, SuccessMessageMixin, CreateView):
    template_name = "conseils/demande_form.html"
    form_class = DemandeConseilForm
    success_message = "Votre demande a été transmise aux experts."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["ferme"] = self.request.user.ferme
        return kwargs

    def form_valid(self, form):
        form.instance.fermier = self.request.user
        return super().form_valid(form)


class DemandeCloturerView(FermierRequisMixin, View):
    def post(self, request, pk):
        demande = get_object_or_404(DemandeConseil, pk=pk, fermier=request.user)
        demande.statut = Statut.CLOTUREE
        demande.save(update_fields=["statut", "date_maj"])
        messages.success(request, "Demande clôturée. Merci !")
        return redirect(demande)


class FichesListView(LoginRequiredMixin, ListView):
    """Bibliothèque de fiches techniques, consultable par tout utilisateur connecté."""

    template_name = "conseils/fiches_liste.html"
    context_object_name = "fiches"
    paginate_by = 9

    def get_queryset(self):
        qs = FicheTechnique.objects.filter(publiee=True).select_related("auteur")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(titre__icontains=q) | Q(resume__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class FicheDetailView(LoginRequiredMixin, DetailView):
    template_name = "conseils/fiche_detail.html"

    def get_queryset(self):
        user = self.request.user
        qs = FicheTechnique.objects.select_related("auteur")
        # Les brouillons ne sont visibles que de leur auteur
        return qs.filter(Q(publiee=True) | Q(auteur=user))


# ---------------------------------------------------------------------------
# Détail et fil de discussion (fermier propriétaire OU expert concerné)
# ---------------------------------------------------------------------------
class DemandeDetailView(LoginRequiredMixin, DetailView):
    template_name = "conseils/demande_detail.html"
    model = DemandeConseil

    def get_object(self, queryset=None):
        demande = super().get_object(queryset)
        user = self.request.user
        profil = getattr(user, "profil", None)
        autorise = (
            demande.fermier_id == user.pk
            or (profil and profil.est_expert and profil.est_valide
                and (demande.expert_id in (None, user.pk)))
        )
        if not autorise:
            raise PermissionDenied
        return demande

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        d = self.object
        ctx["form"] = ReponseForm()
        ctx["est_proprietaire"] = d.fermier_id == self.request.user.pk
        ctx["peut_repondre"] = d.statut != Statut.CLOTUREE and (
            ctx["est_proprietaire"] or d.expert_id == self.request.user.pk)
        return ctx

    def post(self, request, *args, **kwargs):
        """Ajoute un message au fil. Le premier message de l'expert passe la demande à REPONDUE."""
        self.object = demande = self.get_object()
        form = ReponseForm(request.POST)
        if demande.statut == Statut.CLOTUREE:
            raise PermissionDenied
        est_expert_assigne = demande.expert_id == request.user.pk
        if demande.fermier_id != request.user.pk and not est_expert_assigne:
            raise PermissionDenied
        if form.is_valid():
            reponse = form.save(commit=False)
            reponse.demande, reponse.auteur = demande, request.user
            reponse.save()
            if est_expert_assigne and demande.statut == Statut.PRISE_EN_CHARGE:
                demande.statut = Statut.REPONDUE
            elif not est_expert_assigne and demande.statut == Statut.REPONDUE:
                demande.statut = Statut.PRISE_EN_CHARGE  # le fermier relance
            demande.save()
            messages.success(request, "Message envoyé.")
            return redirect(demande)
        ctx = self.get_context_data(object=demande)
        ctx["form"] = form
        return self.render_to_response(ctx)


# ---------------------------------------------------------------------------
# Côté expert
# ---------------------------------------------------------------------------
class ExpertTableauBordView(ExpertRequisMixin, TemplateView):
    template_name = "conseils/expert_tableau_bord.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["a_traiter"] = DemandeConseil.objects.filter(
            statut=Statut.OUVERTE).select_related("fermier").order_by("-urgence", "date_creation")[:6]
        ctx["en_cours"] = DemandeConseil.objects.filter(
            expert=u, statut__in=[Statut.PRISE_EN_CHARGE, Statut.REPONDUE]).select_related("fermier")
        ctx["nb_traitees"] = DemandeConseil.objects.filter(expert=u, statut=Statut.CLOTUREE).count()
        ctx["nb_fiches"] = FicheTechnique.objects.filter(auteur=u).count()
        ctx["nb_ouvertes"] = DemandeConseil.objects.filter(statut=Statut.OUVERTE).count()
        return ctx


class DemandesOuvertesView(ExpertRequisMixin, ListView):
    template_name = "conseils/demandes_ouvertes.html"
    context_object_name = "demandes"
    paginate_by = 12

    def get_queryset(self):
        return DemandeConseil.objects.filter(statut=Statut.OUVERTE).select_related(
            "fermier").order_by("-urgence", "date_creation")


class MesTraitementsView(ExpertRequisMixin, ListView):
    template_name = "conseils/mes_traitements.html"
    context_object_name = "demandes"
    paginate_by = 12

    def get_queryset(self):
        return DemandeConseil.objects.filter(expert=self.request.user).select_related("fermier")


class DemandePrendreView(ExpertRequisMixin, View):
    """Un expert s'attribue une demande ouverte (règle RG-09 : un seul expert par demande)."""

    def post(self, request, pk):
        demande = get_object_or_404(DemandeConseil, pk=pk)
        if demande.statut != Statut.OUVERTE or demande.expert_id:
            messages.warning(request, "Cette demande est déjà prise en charge.")
            return redirect("conseils:demandes_ouvertes")
        demande.expert, demande.statut = request.user, Statut.PRISE_EN_CHARGE
        demande.save()
        messages.success(request, "Demande prise en charge.")
        return redirect(demande)


class FicheCreerView(ExpertRequisMixin, SuccessMessageMixin, CreateView):
    template_name = "conseils/fiche_form.html"
    form_class = FicheTechniqueForm
    success_url = reverse_lazy("conseils:mes_fiches")
    success_message = "Fiche technique enregistrée."

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)


class MesFichesView(ExpertRequisMixin, ListView):
    template_name = "conseils/mes_fiches.html"
    context_object_name = "fiches"

    def get_queryset(self):
        return FicheTechnique.objects.filter(auteur=self.request.user)


class _FicheAuteurMixin(ExpertRequisMixin):
    def get_queryset(self):
        return FicheTechnique.objects.filter(auteur=self.request.user)


class FicheModifierView(_FicheAuteurMixin, SuccessMessageMixin, UpdateView):
    template_name = "conseils/fiche_form.html"
    form_class = FicheTechniqueForm
    success_url = reverse_lazy("conseils:mes_fiches")
    success_message = "Fiche mise à jour."


class FicheSupprimerView(_FicheAuteurMixin, DeleteView):
    template_name = "crud/confirmation_suppression.html"
    success_url = reverse_lazy("conseils:mes_fiches")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(titre_singulier="Fiche technique", prefixe="fiche",
                   annuler_url=reverse_lazy("conseils:mes_fiches"))
        return ctx
