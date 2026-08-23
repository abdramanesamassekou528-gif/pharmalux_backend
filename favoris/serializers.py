from rest_framework import serializers
from catalogue.serializers import ProduitListSerializer
from catalogue.models import Produit
from .models import Favori


class FavoriSerializer(serializers.ModelSerializer):
    produit = ProduitListSerializer(read_only=True)
    productId = serializers.PrimaryKeyRelatedField(source='produit', queryset=Produit.objects.all(), write_only=True)

    class Meta:
        model = Favori
        fields = ['id', 'produit', 'productId', 'cree_le']
