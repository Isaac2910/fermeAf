"""Modèles de l'application « conseils » : demandes d'expertise et fiches techniques."""
from django.conf import settings
from django.db import models
from django.urls import reverse

from exploitation.models import Culture, Troupeau


class DemandeConseil(models.Model):
    """Demande d'un fermier adressée aux experts.

    Cycle de vie : OUVERTE -> PRISE_EN_CHARGE (expert assigné) -> REPONDUE -> CLOTUREE.
    """

    class Categorie(models.TextChoices):
        CULTURE = "CULTURE", "Culture / agronomie"
        ELEVAGE = "ELEVAGE", "Élevage"
        SOL = "SOL", "Sol et fertilisation"
        MALADIE = "MALADIE", "Maladie / ravageur"
        GESTION = "GESTION", "Gestion de l'exploitation"
        AUTRE = "AUTRE", "Autre"

    class Statut(models.TextChoices):
        OUVERTE = "OUVERTE", "Ouverte"
        PRISE_EN_CHARGE = "PRISE_EN_CHARGE", "Prise en charge"
        REPONDUE = "REPONDUE", "Répondue"
        CLOTUREE = "CLOTUREE", "Clôturée"

    class Urgence(models.TextChoices):
        NORMALE = "NORMALE", "Normale"
        URGENTE = "URGENTE", "Urgente"

    fermier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="demandes_emises")
    expert = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="demandes_traitees")
    titre = models.CharField("Objet", max_length=150)
    categorie = models.CharField("Catégorie", max_length=10, choices=Categorie.choices)
    urgence = models.CharField("Urgence", max_length=8, choices=Urgence.choices,
                               default=Urgence.NORMALE)
    description = models.TextField("Description du problème")
    culture = models.ForeignKey(Culture, null=True, blank=True, on_delete=models.SET_NULL,
                                verbose_name="Culture concernée")
    troupeau = models.ForeignKey(Troupeau, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name="Troupeau concerné")
    photo = models.ImageField("Photo (facultatif)", upload_to="demandes/", blank=True)
    statut = models.CharField("Statut", max_length=16, choices=Statut.choices,
                              default=Statut.OUVERTE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Demande de conseil"
        verbose_name_plural = "Demandes de conseil"

    def __str__(self):
        return f"#{self.pk} - {self.titre}"

    def get_absolute_url(self):
        return reverse("conseils:demande_detail", args=[self.pk])


class Reponse(models.Model):
    """Message du fil de discussion d'une demande (fermier ou expert)."""

    demande = models.ForeignKey(DemandeConseil, on_delete=models.CASCADE,
                                related_name="reponses")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contenu = models.TextField("Message")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"Réponse de {self.auteur} le {self.date:%d/%m/%Y}"


class FicheTechnique(models.Model):
    """Fiche de bonnes pratiques rédigée par un expert, lisible par tous les fermiers."""

    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name="fiches")
    titre = models.CharField("Titre", max_length=150)
    categorie = models.CharField("Catégorie", max_length=10,
                                 choices=DemandeConseil.Categorie.choices)
    resume = models.CharField("Résumé", max_length=250)
    contenu = models.TextField("Contenu")
    publiee = models.BooleanField("Publiée", default=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_publication"]
        verbose_name = "Fiche technique"
        verbose_name_plural = "Fiches techniques"

    def __str__(self):
        return self.titre
