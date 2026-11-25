from django.contrib import admin

from .models import DemandeConseil, FicheTechnique, Reponse


class ReponseInline(admin.TabularInline):
    model = Reponse
    extra = 0


@admin.register(DemandeConseil)
class DemandeConseilAdmin(admin.ModelAdmin):
    list_display = ("id", "titre", "fermier", "expert", "categorie", "urgence", "statut",
                    "date_creation")
    list_filter = ("statut", "categorie", "urgence")
    search_fields = ("titre", "description", "fermier__username")
    inlines = [ReponseInline]
    date_hierarchy = "date_creation"


@admin.register(FicheTechnique)
class FicheTechniqueAdmin(admin.ModelAdmin):
    list_display = ("titre", "auteur", "categorie", "publiee", "date_publication")
    list_filter = ("categorie", "publiee")
    search_fields = ("titre", "resume")
