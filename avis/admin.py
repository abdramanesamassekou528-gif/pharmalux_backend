from django.contrib import admin
from .models import Avis


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['produit', 'utilisateur', 'note', 'verifie', 'signale', 'cree_le']
    list_filter = ['note', 'verifie', 'signale']
    search_fields = ['produit__nom', 'utilisateur__email', 'commentaire']
    actions = ['approuver', 'marquer_signale']

    @admin.action(description='Lever le signalement')
    def approuver(self, request, queryset):
        queryset.update(signale=False)

    @admin.action(description='Signaler (masquer du site)')
    def marquer_signale(self, request, queryset):
        queryset.update(signale=True)
