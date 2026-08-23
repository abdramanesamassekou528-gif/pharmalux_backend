from rest_framework import serializers
from .models import Categorie, SousCategorie, Marque, Produit, ProduitImage


class SousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields = ['slug', 'nom']


class CategorieSerializer(serializers.ModelSerializer):
    sousCategories = SousCategorieSerializer(source='sous_categories', many=True, read_only=True)
    icon = serializers.CharField(source='icone')

    class Meta:
        model = Categorie
        fields = ['slug', 'nom', 'icon', 'couleur', 'sousCategories']


class MarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marque
        fields = ['nom']


class ProduitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduitImage
        fields = ['image', 'ordre']


class ProduitListSerializer(serializers.ModelSerializer):
    """Forme allégée utilisée dans les listes (catalogue, carrousels)."""
    marque = serializers.CharField(source='marque.nom')
    categorie = serializers.CharField(source='categorie.slug')
    sousCategorie = serializers.CharField(source='sous_categorie.slug', default=None)
    ancienPrix = serializers.IntegerField(source='ancien_prix')
    reduction = serializers.IntegerField(source='reduction_pourcentage')
    avisCount = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    tags = serializers.ListField(read_only=True)
    images = ProduitImageSerializer(many=True, read_only=True)

    class Meta:
        model = Produit
        fields = [
            'id', 'slug', 'nom', 'marque', 'categorie', 'sousCategorie',
            'prix', 'ancienPrix', 'reduction', 'stock', 'sku',
            'note', 'avisCount', 'tags', 'images',
        ]

    def get_note(self, obj):
        return round(getattr(obj, 'note_moyenne', None) or 0, 1)

    def get_avisCount(self, obj):
        return getattr(obj, 'avis_count', None) or 0


class ProduitDetailSerializer(ProduitListSerializer):
    contenance = serializers.CharField()
    poids = serializers.CharField()
    ageRecommande = serializers.CharField(source='age_recommande')
    modeUtilisation = serializers.CharField(source='mode_utilisation')
    lot = serializers.CharField()
    fabrication = serializers.DateField(source='date_fabrication')
    expiration = serializers.DateField(source='date_expiration')

    class Meta(ProduitListSerializer.Meta):
        fields = ProduitListSerializer.Meta.fields + [
            'contenance', 'poids', 'ageRecommande', 'description', 'composition',
            'modeUtilisation', 'precautions', 'lot', 'fabrication', 'expiration',
        ]
