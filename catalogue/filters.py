import django_filters as filters
from django.db.models import F
from .models import Produit


class ProduitFilter(filters.FilterSet):
    categorie = filters.CharFilter(field_name='categorie__slug')
    sous_categorie = filters.CharFilter(field_name='sous_categorie__slug')
    marque = filters.BaseInFilter(field_name='marque__nom')  # ?marque=Mustela,Nuk
    prix_max = filters.NumberFilter(field_name='prix', lookup_expr='lte')
    en_stock = filters.BooleanFilter(method='filtrer_en_stock')
    promo = filters.BooleanFilter(method='filtrer_promo')
    nouveaute = filters.BooleanFilter(field_name='est_nouveaute')
    bestseller = filters.BooleanFilter(field_name='est_bestseller')

    class Meta:
        model = Produit
        fields = ['categorie', 'sous_categorie', 'marque', 'prix_max', 'en_stock', 'promo', 'nouveaute', 'bestseller']

    def filtrer_en_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset

    def filtrer_promo(self, queryset, name, value):
        return queryset.filter(ancien_prix__gt=F('prix')) if value else queryset
