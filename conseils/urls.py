from django.urls import path

from . import views

app_name = "conseils"

urlpatterns = [
    # Fermier
    path("demandes/", views.MesDemandesView.as_view(), name="mes_demandes"),
    path("demandes/nouvelle/", views.DemandeCreerView.as_view(), name="demande_creer"),
    path("demandes/<int:pk>/cloturer/", views.DemandeCloturerView.as_view(),
         name="demande_cloturer"),
    # Commun fermier / expert
    path("demandes/<int:pk>/", views.DemandeDetailView.as_view(), name="demande_detail"),
    path("fiches/", views.FichesListView.as_view(), name="fiches_liste"),
    path("fiches/<int:pk>/", views.FicheDetailView.as_view(), name="fiche_detail"),
    # Expert
    path("expert/", views.ExpertTableauBordView.as_view(), name="expert_tableau_bord"),
    path("expert/a-traiter/", views.DemandesOuvertesView.as_view(), name="demandes_ouvertes"),
    path("expert/mes-traitements/", views.MesTraitementsView.as_view(), name="mes_traitements"),
    path("expert/demandes/<int:pk>/prendre/", views.DemandePrendreView.as_view(),
         name="demande_prendre"),
    path("expert/fiches/", views.MesFichesView.as_view(), name="mes_fiches"),
    path("expert/fiches/nouvelle/", views.FicheCreerView.as_view(), name="fiche_creer"),
    path("expert/fiches/<int:pk>/modifier/", views.FicheModifierView.as_view(),
         name="fiche_modifier"),
    path("expert/fiches/<int:pk>/supprimer/", views.FicheSupprimerView.as_view(),
         name="fiche_supprimer"),
]
