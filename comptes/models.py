"""Modèles de l'application « comptes » : profil et rôle des utilisateurs."""
from django.conf import settings
from django.db import models


class Profil(models.Model):
    """Extension du modèle User de Django : rôle métier et coordonnées.

    L'administrateur n'a pas de profil métier : il s'appuie sur l'attribut
    natif ``is_staff`` / ``is_superuser`` et sur le site /admin/ de Django.
    """

    class Role(models.TextChoices):
        FERMIER = "FERMIER", "Fermier"
        EXPERT = "EXPERT", "Expert (agronome / vétérinaire)"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil"
    )
    role = models.CharField("Rôle", max_length=10, choices=Role.choices, default=Role.FERMIER)
    telephone = models.CharField("Téléphone", max_length=20, blank=True)
    localite = models.CharField("Localité", max_length=100, blank=True)
    specialite = models.CharField(
        "Spécialité", max_length=120, blank=True,
        help_text="Renseignée pour les experts (ex. : agronomie, santé animale).",
    )
    est_valide = models.BooleanField(
        "Compte validé", default=True,
        help_text="Un compte expert doit être validé par l'administrateur.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def est_fermier(self):
        return self.role == self.Role.FERMIER

    @property
    def est_expert(self):
        return self.role == self.Role.EXPERT
