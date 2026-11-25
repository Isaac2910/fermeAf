from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "comptes"

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("connexion/", views.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", LogoutView.as_view(), name="deconnexion"),
    path("inscription/", views.InscriptionView.as_view(), name="inscription"),
    path("profil/", views.profil, name="profil"),
]
