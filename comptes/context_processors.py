"""Fournit à tous les gabarits le rôle courant et le menu de navigation adapté."""
from django.urls import reverse

MENU_FERMIER = [
    ("Tableau de bord", "exploitation:tableau_bord", "bi-speedometer2"),
    ("Parcelles", "exploitation:parcelle_liste", "bi-grid-3x3-gap"),
    ("Cultures", "exploitation:culture_liste", "bi-flower2"),
    ("Récoltes", "exploitation:recolte_liste", "bi-basket"),
    ("Troupeaux", "exploitation:troupeau_liste", "bi-piggy-bank"),
    ("Soins de santé", "exploitation:soin_liste", "bi-heart-pulse"),
    ("Stock d'intrants", "exploitation:produit_liste", "bi-box-seam"),
    ("Mouvements", "exploitation:mouvement_liste", "bi-arrow-left-right"),
    ("Finances", "exploitation:operation_liste", "bi-cash-coin"),
    ("Tâches", "exploitation:tache_liste", "bi-calendar-check"),
    ("Mes demandes", "conseils:mes_demandes", "bi-chat-left-text"),
    ("Fiches techniques", "conseils:fiches_liste", "bi-journal-text"),
]

MENU_EXPERT = [
    ("Tableau de bord", "conseils:expert_tableau_bord", "bi-speedometer2"),
    ("Demandes à traiter", "conseils:demandes_ouvertes", "bi-inbox"),
    ("Mes traitements", "conseils:mes_traitements", "bi-chat-dots"),
    ("Mes fiches", "conseils:mes_fiches", "bi-journal-plus"),
    ("Bibliothèque", "conseils:fiches_liste", "bi-journal-text"),
]


def navigation(request):
    user = request.user
    role, menu = None, []
    if user.is_authenticated:
        profil = getattr(user, "profil", None)
        if user.is_staff:
            role = "ADMIN"
        elif profil:
            role = profil.role
            modele = MENU_FERMIER if profil.est_fermier else MENU_EXPERT
            for libelle, nom_url, icone in modele:
                url = reverse(nom_url)
                actif = request.path == url or (
                    url.count("/") > 2 and request.path.startswith(url))
                menu.append({"libelle": libelle, "url": url, "icone": icone, "actif": actif})
    return {"role_courant": role, "menu": menu}
