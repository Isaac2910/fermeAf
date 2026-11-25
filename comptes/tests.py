from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from comptes.models import Profil

User = get_user_model()

DONNEES = {"username": "nouveau", "first_name": "Ana", "last_name": "Test",
           "email": "ana@test.ga", "password1": "Complexe2026!x", "password2": "Complexe2026!x"}


class InscriptionTests(TestCase):
    def test_inscription_fermier_cree_profil_et_ferme(self):
        r = self.client.post(reverse("comptes:inscription"), {
            **DONNEES, "role": "FERMIER", "nom_ferme": "Ferme Test", "localite": "Kango"})
        self.assertRedirects(r, reverse("comptes:connexion"))
        u = User.objects.get(username="nouveau")
        self.assertTrue(u.profil.est_valide)
        self.assertEqual(u.ferme.nom, "Ferme Test")

    def test_inscription_expert_en_attente_de_validation(self):
        self.client.post(reverse("comptes:inscription"), {
            **DONNEES, "role": "EXPERT", "specialite": "Agronomie"})
        u = User.objects.get(username="nouveau")
        self.assertFalse(u.profil.est_valide)
        ok = self.client.login(username="nouveau", password="Complexe2026!x")
        self.assertTrue(ok)  # le mot de passe est correct, mais l'accès métier reste bloqué
        self.assertEqual(self.client.get(reverse("conseils:expert_tableau_bord")).status_code, 403)

    def test_formulaire_connexion_refuse_expert_non_valide(self):
        self.client.post(reverse("comptes:inscription"), {
            **DONNEES, "role": "EXPERT", "specialite": "Agronomie"})
        r = self.client.post(reverse("comptes:connexion"), {
            "username": "nouveau", "password": "Complexe2026!x"})
        self.assertContains(r, "en attente de validation")

    def test_fermier_sans_nom_de_ferme_est_refuse(self):
        r = self.client.post(reverse("comptes:inscription"), {**DONNEES, "role": "FERMIER"})
        self.assertFalse(User.objects.filter(username="nouveau").exists())
        self.assertEqual(r.status_code, 200)

    def test_accueil_aiguille_selon_le_role(self):
        u = User.objects.create_user("admin2", password="Motdepasse123!", is_staff=True)
        self.client.login(username="admin2", password="Motdepasse123!")
        self.assertRedirects(self.client.get(reverse("comptes:accueil")), reverse("admin:index"),
                             fetch_redirect_response=False)
