"""Interface d'administration (acteur Administrateur Django) pour les comptes."""
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Profil

User = get_user_model()


class ProfilInline(admin.StackedInline):
    model = Profil
    can_delete = False
    extra = 0


class UtilisateurAdmin(UserAdmin):
    inlines = [ProfilInline]
    list_display = ("username", "first_name", "last_name", "email", "role", "is_staff")
    list_filter = ("is_staff", "is_active", "profil__role", "profil__est_valide")

    @admin.display(description="Rôle", ordering="profil__role")
    def role(self, obj):
        return obj.profil.get_role_display() if hasattr(obj, "profil") else "Administrateur"


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "specialite", "localite", "est_valide", "date_creation")
    list_filter = ("role", "est_valide")
    search_fields = ("user__username", "user__last_name", "specialite", "localite")
    actions = ["valider_comptes", "suspendre_comptes"]

    @admin.action(description="Valider les comptes sélectionnés")
    def valider_comptes(self, request, queryset):
        n = queryset.update(est_valide=True)
        self.message_user(request, f"{n} compte(s) validé(s).", messages.SUCCESS)

    @admin.action(description="Suspendre les comptes sélectionnés")
    def suspendre_comptes(self, request, queryset):
        n = queryset.update(est_valide=False)
        self.message_user(request, f"{n} compte(s) suspendu(s).", messages.WARNING)


admin.site.unregister(User)
admin.site.register(User, UtilisateurAdmin)
