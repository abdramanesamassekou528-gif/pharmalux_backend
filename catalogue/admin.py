from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Categorie, Marque, Produit, ProduitImage, SousCategorie


class SousCategorieInline(admin.TabularInline):
    model = SousCategorie
    extra = 1


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'couleur', 'ordre']
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [SousCategorieInline]


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


class ProduitImageInline(admin.TabularInline):
    model = ProduitImage
    extra = 1


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'sku', 'marque', 'categorie', 'prix', 'badge_stock',
        'badge_expiration', 'est_nouveaute', 'est_bestseller', 'actif',
    ]
    list_filter = ['categorie', 'marque', 'actif', 'est_nouveaute', 'est_bestseller']
    search_fields = ['nom', 'sku', 'lot']
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [ProduitImageInline]
    autocomplete_fields = ['marque']
    fieldsets = (
        ('Identification', {'fields': ('nom', 'slug', 'sku', 'marque', 'categorie', 'sous_categorie', 'actif')}),
        ('Prix & stock', {'fields': ('prix', 'ancien_prix', 'stock', 'seuil_stock_faible')}),
        ('Fiche produit', {'fields': ('contenance', 'poids', 'age_recommande', 'description', 'composition', 'mode_utilisation', 'precautions')}),
        ('Traçabilité', {'fields': ('lot', 'date_fabrication', 'date_expiration')}),
        ('Mise en avant', {'fields': ('est_nouveaute', 'est_bestseller')}),
    )
    actions = ['marquer_bestseller', 'marquer_nouveaute']

    @admin.display(description='Stock')
    def badge_stock(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color:#C6523F;font-weight:600">⚠ Rupture</span>')
        if obj.en_stock_faible:
            return format_html('<span style="color:#D98A2B;font-weight:600">{} — faible</span>', obj.stock)
        return obj.stock

    @admin.display(description='Péremption')
    def badge_expiration(self, obj):
        if not obj.date_expiration:
            return '—'
        jours = (obj.date_expiration - timezone.now().date()).days
        if jours < 0:
            return format_html('<span style="color:#C6523F;font-weight:600">Expiré</span>')
        if jours <= 60:
            return format_html('<span style="color:#D98A2B;font-weight:600">{} (J-{})</span>', obj.date_expiration, jours)
        return obj.date_expiration

    @admin.action(description='Marquer comme best-seller')
    def marquer_bestseller(self, request, queryset):
        queryset.update(est_bestseller=True)

    @admin.action(description='Marquer comme nouveauté')
    def marquer_nouveaute(self, request, queryset):
        queryset.update(est_nouveaute=True)

    def get_search_results(self, request, queryset, search_term):
        # Utilisé par autocomplete_fields ailleurs si besoin.
        return super().get_search_results(request, queryset, search_term)
