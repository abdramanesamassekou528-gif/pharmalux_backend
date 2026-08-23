from django.db import transaction
from rest_framework import serializers

from catalogue.models import Produit
from catalogue.serializers import ProduitListSerializer
from .models import Commande, HistoriqueCommande, LigneCommande, LignePanier, Paiement, Panier, ZoneLivraison

ETAPES_ORDRE = [e for e, _ in Commande.STATUTS if e != 'annulee']


class ZoneLivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZoneLivraison
        fields = ['commune', 'prix', 'delai']


# ---------------------------------------------------------------------------
# Panier serveur
# ---------------------------------------------------------------------------
class LignePanierSerializer(serializers.ModelSerializer):
    produit = ProduitListSerializer(read_only=True)
    productId = serializers.PrimaryKeyRelatedField(source='produit', queryset=Produit.objects.all(), write_only=True)

    class Meta:
        model = LignePanier
        fields = ['id', 'produit', 'productId', 'quantite']


class PanierSerializer(serializers.ModelSerializer):
    lignes = LignePanierSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = ['id', 'lignes', 'maj_le']


# ---------------------------------------------------------------------------
# Commandes
# ---------------------------------------------------------------------------
class LigneCommandeSerializer(serializers.ModelSerializer):
    produit = ProduitListSerializer(read_only=True)
    prixUnitaire = serializers.IntegerField(source='prix_unitaire', read_only=True)

    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'prixUnitaire']


class HistoriqueEtapeSerializer(serializers.Serializer):
    """Reconstruit la timeline complète (les 6 étapes, faites ou non) à
    partir des seules lignes HistoriqueCommande réellement enregistrées —
    exactement la forme consommée par <OrderStatusTimeline> côté frontend."""
    etape = serializers.CharField()
    date = serializers.DateTimeField(allow_null=True)
    fait = serializers.BooleanField()


class CommandeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='reference', read_only=True)
    articles = LigneCommandeSerializer(many=True, read_only=True)
    adresse = serializers.CharField(source='adresse_texte')
    modeLivraison = serializers.CharField(source='get_mode_livraison_display', read_only=True)
    modePaiement = serializers.SerializerMethodField()
    historique = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='cree_le', format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Commande
        fields = ['id', 'date', 'statut', 'total', 'sous_total', 'reduction', 'adresse',
                   'modeLivraison', 'modePaiement', 'articles', 'historique']

    def get_modePaiement(self, obj):
        return obj.paiement.get_methode_display() if hasattr(obj, 'paiement') else None

    def get_historique(self, obj):
        faites = {h.etape: h.date for h in obj.historique.all()}
        return [
            {'etape': etape, 'date': faites.get(etape), 'fait': etape in faites}
            for etape in ETAPES_ORDRE
        ]


class CreerCommandeSerializer(serializers.Serializer):
    """POST /api/commandes/ — reçoit exactement la forme envoyée par
    `placeOrder()` côté frontend (zone, mode, méthode, adresse, coupon)."""
    zone = serializers.CharField()
    adresse_detail = serializers.CharField(required=False, allow_blank=True, default='')
    mode_livraison = serializers.ChoiceField(choices=[c for c, _ in Commande.MODES_LIVRAISON])
    methode_paiement = serializers.ChoiceField(choices=[c for c, _ in Paiement.METHODES])
    code_coupon = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_zone(self, valeur):
        try:
            return ZoneLivraison.objects.get(commune=valeur, active=True)
        except ZoneLivraison.DoesNotExist:
            raise serializers.ValidationError("Zone de livraison inconnue.")

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        utilisateur = request.user
        panier, _ = Panier.objects.get_or_create(utilisateur=utilisateur)
        lignes = list(panier.lignes.select_related('produit').all())
        if not lignes:
            raise serializers.ValidationError('Le panier est vide.')

        zone = validated_data['zone']
        for ligne in lignes:
            if ligne.quantite > ligne.produit.stock:
                raise serializers.ValidationError(
                    f"Stock insuffisant pour « {ligne.produit.nom} » (disponible : {ligne.produit.stock})."
                )
        sous_total = sum(l.produit.prix * l.quantite for l in lignes)

        reduction = 0
        coupon = None
        code = validated_data.get('code_coupon', '').strip()
        if code:
            from promotions.models import Coupon, UtilisationCoupon
            try:
                coupon = Coupon.objects.get(code__iexact=code, actif=True)
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({'code_coupon': 'Code promo invalide ou expiré.'})
            if UtilisationCoupon.objects.filter(coupon=coupon, utilisateur=utilisateur).exists():
                raise serializers.ValidationError({'code_coupon': 'Ce code a déjà été utilisé.'})
            if coupon.reduction_pourcentage:
                reduction = round(sous_total * coupon.reduction_pourcentage / 100)
            elif coupon.reduction_montant:
                reduction = min(coupon.reduction_montant, sous_total)

        total = max(sous_total - reduction, 0) + zone.prix

        commande = Commande.objects.create(
            utilisateur=utilisateur,
            adresse_texte=f"{zone.commune}" + (f", {validated_data['adresse_detail']}" if validated_data.get('adresse_detail') else ''),
            mode_livraison=validated_data['mode_livraison'],
            frais_livraison=zone.prix,
            coupon=coupon,
            sous_total=sous_total,
            reduction=reduction,
            total=total,
        )
        HistoriqueCommande.objects.create(commande=commande, etape='commande_confirmee')

        for ligne in lignes:
            LigneCommande.objects.create(
                commande=commande, produit=ligne.produit,
                quantite=ligne.quantite, prix_unitaire=ligne.produit.prix,
            )
            Produit.objects.filter(pk=ligne.produit_id).update(stock=ligne.produit.stock - ligne.quantite)

        Paiement.objects.create(
            commande=commande, methode=validated_data['methode_paiement'],
            montant=total,
            statut='en_attente' if validated_data['methode_paiement'] != 'livraison' else 'en_attente',
        )

        if coupon:
            from promotions.models import UtilisationCoupon
            UtilisationCoupon.objects.create(coupon=coupon, utilisateur=utilisateur, commande=commande)

        panier.lignes.all().delete()
        return commande
