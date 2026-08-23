from django.contrib import admin
from .models import Favori


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'produit', 'cree_le']
    search_fields = ['utilisateur__email', 'produit__nom']
