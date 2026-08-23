from django.contrib import admin
from django.utils.html import format_html
from .models import Commande, HistoriqueCommande, LigneCommande, LignePanier, Paiement, Panier, ZoneLivraison

STATUT_COULEURS = {
    'commande_confirmee': '#4C8B97', 'paiement_confirme': '#547A3F', 'preparation': '#D98A2B',
    'expedition': '#8C6FBD', 'en_livraison': '#F26F41', 'livree': '#547A3F', 'annulee': '#C6523F',
}


@admin.register(ZoneLivraison)
class ZoneLivraisonAdmin(admin.ModelAdmin):
    list_display = ['commune', 'prix', 'delai', 'active', 'ordre']
    list_editable = ['active', 'ordre']


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['produit', 'quantite', 'prix_unitaire']
    can_delete = False


class PaiementInline(admin.StackedInline):
    model = Paiement
    extra = 0


class HistoriqueInline(admin.TabularInline):
    model = HistoriqueCommande
    extra = 0
    readonly_fields = ['date']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['reference', 'utilisateur', 'badge_statut', 'total', 'mode_livraison', 'cree_le']
    list_filter = ['statut', 'mode_livraison']
    search_fields = ['reference', 'utilisateur__email']
    readonly_fields = ['reference', 'sous_total', 'reduction', 'total', 'cree_le', 'maj_le']
    inlines = [LigneCommandeInline, PaiementInline, HistoriqueInline]
    actions = ['avancer_a_preparation', 'avancer_a_expedition', 'avancer_a_en_livraison', 'avancer_a_livree', 'annuler']

    @admin.display(description='Statut')
    def badge_statut(self, obj):
        couleur = STATUT_COULEURS.get(obj.statut, '#6B7060')
        return format_html('<span style="color:{};font-weight:700">{}</span>', couleur, obj.get_statut_display())

    def _avancer(self, request, queryset, statut):
        for commande in queryset:
            commande.avancer_statut(statut)

    @admin.action(description='→ Marquer « Préparation »')
    def avancer_a_preparation(self, request, queryset):
        self._avancer(request, queryset, 'preparation')

    @admin.action(description='→ Marquer « Expédition »')
    def avancer_a_expedition(self, request, queryset):
        self._avancer(request, queryset, 'expedition')

    @admin.action(description='→ Marquer « En livraison »')
    def avancer_a_en_livraison(self, request, queryset):
        self._avancer(request, queryset, 'en_livraison')

    @admin.action(description='→ Marquer « Livrée »')
    def avancer_a_livree(self, request, queryset):
        self._avancer(request, queryset, 'livree')

    @admin.action(description='Annuler la commande')
    def annuler(self, request, queryset):
        queryset.update(statut='annulee')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['commande', 'methode', 'statut', 'montant', 'cree_le']
    list_filter = ['methode', 'statut']
    search_fields = ['commande__reference', 'reference_transaction']


class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 0


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'maj_le']
    inlines = [LignePanierInline]
