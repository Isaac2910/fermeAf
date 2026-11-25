"""Formulaires de l'application « conseils »."""
from django import forms

from comptes.forms import BootstrapFormMixin
from exploitation.models import Culture, Troupeau

from .models import DemandeConseil, FicheTechnique, Reponse


class DemandeConseilForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = DemandeConseil
        fields = ("titre", "categorie", "urgence", "description", "culture", "troupeau",
                  "photo")

    def __init__(self, *args, ferme=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["culture"].queryset = Culture.objects.filter(parcelle__ferme=ferme)
        self.fields["troupeau"].queryset = Troupeau.objects.filter(ferme=ferme)

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "size") and photo.size > 3 * 1024 * 1024:
            raise forms.ValidationError("La photo ne doit pas dépasser 3 Mo.")
        return photo


class ReponseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ("contenu",)
        labels = {"contenu": "Votre message"}
        widgets = {"contenu": forms.Textarea(attrs={"rows": 4})}


class FicheTechniqueForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = FicheTechnique
        fields = ("titre", "categorie", "resume", "contenu", "publiee")
        widgets = {"contenu": forms.Textarea(attrs={"rows": 10})}
