from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from commandes.models import Panier
from .models import Coupon, UtilisationCoupon
from .serializers import CouponSerializer


class CouponListeView(APIView):
    """GET /api/coupons/ — coupons actifs, avec indicateur 'utilise' pour l'utilisateur connecté."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Coupon.objects.filter(actif=True, expire_le__gte=timezone.now().date())
        return Response(CouponSerializer(qs, many=True, context={'request': request}).data)


class AppliquerCouponView(APIView):
    """POST /api/coupons/appliquer/ { code } — valide un code pour le panier courant."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = (request.data.get('code') or '').strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code, actif=True, expire_le__gte=timezone.now().date())
        except Coupon.DoesNotExist:
            return Response({'valide': False, 'message': 'Code promo introuvable ou expiré.'})

        if UtilisationCoupon.objects.filter(coupon=coupon, utilisateur=request.user).exists():
            return Response({'valide': False, 'message': 'Ce code a déjà été utilisé.'})

        panier = Panier.objects.filter(utilisateur=request.user).first()
        sous_total = sum(l.produit.prix * l.quantite for l in panier.lignes.all()) if panier else 0
        if sous_total < coupon.montant_minimum:
            return Response({
                'valide': False,
                'message': f"Ce code nécessite un panier d'au moins {coupon.montant_minimum} FCFA.",
            })

        return Response({'valide': True, 'coupon': CouponSerializer(coupon, context={'request': request}).data})
