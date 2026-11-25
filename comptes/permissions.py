"""Contrôle d'accès par rôle (fermier / expert) pour les vues basées sur les classes."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Profil


class RoleRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Autorise uniquement les utilisateurs dont le profil porte le rôle requis.

    - utilisateur non connecté  -> redirection vers la page de connexion ;
    - connecté mais mauvais rôle -> erreur HTTP 403 (gabarit 403.html).
    """

    role_requis = None

    def test_func(self):
        user = self.request.user
        profil = getattr(user, "profil", None)
        return bool(profil and profil.est_valide and profil.role == self.role_requis)


class FermierRequisMixin(RoleRequisMixin):
    role_requis = Profil.Role.FERMIER


class ExpertRequisMixin(RoleRequisMixin):
    role_requis = Profil.Role.EXPERT
