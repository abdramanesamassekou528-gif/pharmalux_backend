from rest_framework import serializers
from .models import Avis


class AvisSerializer(serializers.ModelSerializer):
    productId = serializers.PrimaryKeyRelatedField(source='produit', queryset=Avis._meta.get_field('produit').related_model.objects.all())
    auteur = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='cree_le', format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Avis
        fields = ['id', 'productId', 'auteur', 'note', 'commentaire', 'photo', 'verifie', 'signale', 'date']
        read_only_fields = ['verifie', 'signale']

    def get_auteur(self, obj):
        prenom = obj.utilisateur.first_name
        return prenom or obj.utilisateur.email.split('@')[0]

    def validate_productId(self, produit):
        request = self.context['request']
        deja_pose = Avis.objects.filter(produit=produit, utilisateur=request.user)
        if self.instance:
            deja_pose = deja_pose.exclude(pk=self.instance.pk)
        if deja_pose.exists():
            raise serializers.ValidationError("Vous avez déjà donné votre avis sur ce produit.")
        return produit

    def create(self, validated_data):
        utilisateur = self.context['request'].user
        produit = validated_data['produit']
        # Achat vérifié : l'utilisateur a-t-il une commande livrée contenant ce produit ?
        from commandes.models import LigneCommande
        verifie = LigneCommande.objects.filter(
            commande__utilisateur=utilisateur,
            commande__statut='livree',
            produit=produit,
        ).exists()
        return Avis.objects.create(utilisateur=utilisateur, verifie=verifie, **validated_data)
