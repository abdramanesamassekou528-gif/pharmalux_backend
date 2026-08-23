from django.db.models import Prefetch
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogue.models import Produit
from .models import Commande, HistoriqueCommande, LignePanier, Panier, ZoneLivraison
from .serializers import (
    CommandeSerializer, CreerCommandeSerializer, LignePanierSerializer,
    PanierSerializer, ZoneLivraisonSerializer,
)


class ZoneLivraisonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ZoneLivraison.objects.filter(active=True)
    serializer_class = ZoneLivraisonSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PanierView(APIView):
    """
    GET    /api/panier/                     mon panier serveur
    POST   /api/panier/lignes/               ajouter/mettre à jour une ligne { productId, quantite }
    DELETE /api/panier/lignes/<produit_id>/  retirer une ligne
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        return Response(PanierSerializer(panier).data)


class LignePanierView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        produit_id = request.data.get('productId')
        quantite = int(request.data.get('quantite', 1))
        produit = Produit.objects.filter(pk=produit_id).first()
        if not produit:
            return Response({'detail': 'Produit introuvable.'}, status=404)
        ligne, cree = LignePanier.objects.get_or_create(panier=panier, produit=produit, defaults={'quantite': quantite})
        if not cree:
            ligne.quantite = quantite
            ligne.save()
        return Response(LignePanierSerializer(ligne).data, status=201 if cree else 200)

    def delete(self, request, produit_id):
        Panier.objects.filter(utilisateur=request.user).first() and LignePanier.objects.filter(
            panier__utilisateur=request.user, produit_id=produit_id
        ).delete()
        return Response(status=204)


class CommandeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/commandes/         mes commandes
    GET  /api/commandes/{ref}/   détail + timeline
    POST /api/commandes/         passer commande à partir du panier serveur
    """
    serializer_class = CommandeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'reference'

    def get_queryset(self):
        return Commande.objects.filter(utilisateur=self.request.user).prefetch_related(
            'articles__produit__marque', 'articles__produit__categorie', 'historique', 'paiement'
        )

    def create(self, request, *args, **kwargs):
        serializer = CreerCommandeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        commande = serializer.save()
        return Response(CommandeSerializer(commande).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def avancer(self, request, reference=None):
        """Réservé au staff (back-office) : fait passer la commande à l'étape suivante."""
        commande = self.get_object()
        nouveau_statut = request.data.get('statut')
        if nouveau_statut not in dict(Commande.STATUTS):
            return Response({'detail': 'Statut invalide.'}, status=400)
        commande.avancer_statut(nouveau_statut)
        return Response(CommandeSerializer(commande).data)
