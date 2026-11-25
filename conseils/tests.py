"""Tests du workflow de conseil : demande -> prise en charge -> réponse -> clôture."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from comptes.models import Profil
from conseils.models import DemandeConseil
from exploitation.models import Ferme

User = get_user_model()
MDP = "Motdepasse123!"


def utilisateur(nom, role, valide=True):
    u = User.objects.create_user(nom, password=MDP)
    Profil.objects.create(user=u, role=role, est_valide=valide)
    if role == Profil.Role.FERMIER:
        Ferme.objects.create(proprietaire=u, nom=f"Ferme {nom}", localisation="Ntoum")
    return u


class WorkflowTests(TestCase):
    def setUp(self):
        self.fermier = utilisateur("fermier", "FERMIER")
        self.expert = utilisateur("expert", "EXPERT")
        self.autre_expert = utilisateur("expert2", "EXPERT")
        self.autre_fermier = utilisateur("voisin", "FERMIER")

    def _creer_demande(self):
        self.client.login(username="fermier", password=MDP)
        self.client.post(reverse("conseils:demande_creer"), {
            "titre": "Taches sur les feuilles", "categorie": "MALADIE", "urgence": "NORMALE",
            "description": "Des taches brunes apparaissent."})
        self.client.logout()
        return DemandeConseil.objects.get()

    def test_cycle_de_vie_complet(self):
        demande = self._creer_demande()
        self.assertEqual(demande.statut, "OUVERTE")
        # L'expert prend en charge
        self.client.login(username="expert", password=MDP)
        self.client.post(reverse("conseils:demande_prendre", args=[demande.pk]))
        demande.refresh_from_db()
        self.assertEqual((demande.statut, demande.expert), ("PRISE_EN_CHARGE", self.expert))
        # Il répond
        self.client.post(demande.get_absolute_url(), {"contenu": "Appliquez un fongicide cuprique."})
        demande.refresh_from_db()
        self.assertEqual(demande.statut, "REPONDUE")
        self.assertEqual(demande.reponses.count(), 1)
        self.client.logout()
        # Le fermier clôture
        self.client.login(username="fermier", password=MDP)
        self.client.post(reverse("conseils:demande_cloturer", args=[demande.pk]))
        demande.refresh_from_db()
        self.assertEqual(demande.statut, "CLOTUREE")

    def test_deux_experts_ne_peuvent_pas_prendre_la_meme_demande(self):
        demande = self._creer_demande()
        self.client.login(username="expert", password=MDP)
        self.client.post(reverse("conseils:demande_prendre", args=[demande.pk]))
        self.client.logout()
        self.client.login(username="expert2", password=MDP)
        self.client.post(reverse("conseils:demande_prendre", args=[demande.pk]))
        demande.refresh_from_db()
        self.assertEqual(demande.expert, self.expert)

    def test_un_autre_fermier_ne_voit_pas_la_demande(self):
        demande = self._creer_demande()
        self.client.login(username="voisin", password=MDP)
        self.assertEqual(self.client.get(demande.get_absolute_url()).status_code, 403)

    def test_un_expert_non_assigne_ne_peut_pas_repondre(self):
        demande = self._creer_demande()
        self.client.login(username="expert", password=MDP)
        self.client.post(reverse("conseils:demande_prendre", args=[demande.pk]))
        self.client.logout()
        self.client.login(username="expert2", password=MDP)
        r = self.client.post(demande.get_absolute_url(), {"contenu": "Intrusion"})
        self.assertEqual(r.status_code, 403)

    def test_fermier_ne_peut_pas_creer_de_fiche(self):
        self.client.login(username="fermier", password=MDP)
        self.assertEqual(self.client.get(reverse("conseils:fiche_creer")).status_code, 403)

    def test_expert_cree_une_fiche_visible_par_les_fermiers(self):
        self.client.login(username="expert", password=MDP)
        self.client.post(reverse("conseils:fiche_creer"), {
            "titre": "Fiche test", "categorie": "CULTURE", "resume": "Résumé", "contenu": "Corps",
            "publiee": "on"})
        self.client.logout()
        self.client.login(username="fermier", password=MDP)
        self.assertContains(self.client.get(reverse("conseils:fiches_liste")), "Fiche test")
