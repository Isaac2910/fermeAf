"""Vues d'authentification, d'inscription et d'aiguillage par rôle."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ConnexionForm, InscriptionForm, ProfilForm
from .models import Profil


class ConnexionView(LoginView):
    template_name = "comptes/connexion.html"
    authentication_form = ConnexionForm
    redirect_authenticated_user = True


class InscriptionView(CreateView):
    template_name = "comptes/inscription.html"
    form_class = InscriptionForm
    success_url = reverse_lazy("comptes:connexion")

    def form_valid(self, form):
        reponse = super().form_valid(form)
        if form.cleaned_data["role"] == Profil.Role.EXPERT:
            messages.info(self.request, "Compte expert créé. Il sera activé après validation "
                                        "par l'administrateur.")
        else:
            messages.success(self.request, "Compte créé : vous pouvez vous connecter.")
        return reponse


@login_required
def accueil(request):
    """Aiguille l'utilisateur vers son tableau de bord selon son rôle."""
    user = request.user
    if user.is_staff:
        return redirect("admin:index")
    profil = getattr(user, "profil", None)
    if profil and profil.est_fermier:
        return redirect("exploitation:tableau_bord")
    if profil and profil.est_expert:
        return redirect("conseils:expert_tableau_bord")
    return render(request, "403.html", status=403)


@login_required
def profil(request):
    instance = getattr(request.user, "profil", None)
    if instance is None:  # administrateur sans profil métier
        return redirect("admin:index")
    form = ProfilForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect("comptes:profil")
    return render(request, "comptes/profil.html", {"form": form})
