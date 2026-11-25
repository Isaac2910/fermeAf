"""Formulaires de l'application « comptes » et mixin d'habillage Bootstrap."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profil

User = get_user_model()


class BootstrapFormMixin:
    """Applique les classes Bootstrap 5 et le widget date HTML5 à tous les champs."""

    def _habiller(self):
        for champ in self.fields.values():
            widget = champ.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = "form-select"
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs["class"] = "form-control"
            else:
                widget.attrs["class"] = "form-control"
            if isinstance(champ, forms.DateField):
                champ.widget = forms.DateInput(
                    attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"
                )
            if isinstance(widget, forms.Textarea):
                widget.attrs["rows"] = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._habiller()


class ConnexionForm(BootstrapFormMixin, AuthenticationForm):
    """Refuse la connexion d'un expert dont le compte n'est pas encore validé."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        profil = getattr(user, "profil", None)
        if profil and not profil.est_valide:
            raise forms.ValidationError(
                "Votre compte expert est en attente de validation par l'administrateur.",
                code="en_attente",
            )


class InscriptionForm(BootstrapFormMixin, UserCreationForm):
    """Inscription d'un fermier (création immédiate de sa ferme) ou d'un expert."""

    first_name = forms.CharField(label="Prénom", max_length=60)
    last_name = forms.CharField(label="Nom", max_length=60)
    email = forms.EmailField(label="Adresse e-mail")
    role = forms.ChoiceField(label="Je suis", choices=Profil.Role.choices)
    telephone = forms.CharField(label="Téléphone", max_length=20, required=False)
    localite = forms.CharField(label="Localité", max_length=100, required=False)
    specialite = forms.CharField(label="Spécialité (experts)", max_length=120, required=False)
    nom_ferme = forms.CharField(label="Nom de la ferme (fermiers)", max_length=120, required=False)
    localisation_ferme = forms.CharField(label="Localisation de la ferme", max_length=160,
                                         required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean(self):
        data = super().clean()
        role = data.get("role")
        if role == Profil.Role.FERMIER and not data.get("nom_ferme"):
            self.add_error("nom_ferme", "Indiquez le nom de votre ferme.")
        if role == Profil.Role.EXPERT and not data.get("specialite"):
            self.add_error("specialite", "Indiquez votre spécialité.")
        return data

    def save(self, commit=True):
        from exploitation.models import Ferme  # import local : évite une dépendance circulaire

        user = super().save(commit=commit)
        d = self.cleaned_data
        est_fermier = d["role"] == Profil.Role.FERMIER
        Profil.objects.create(
            user=user, role=d["role"], telephone=d["telephone"], localite=d["localite"],
            specialite=d["specialite"], est_valide=est_fermier,
        )
        if est_fermier:
            Ferme.objects.create(
                proprietaire=user, nom=d["nom_ferme"],
                localisation=d["localisation_ferme"] or d["localite"],
            )
        return user


class ProfilForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profil
        fields = ("telephone", "localite", "specialite")
