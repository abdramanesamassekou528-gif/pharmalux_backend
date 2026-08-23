from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CommandeViewSet, LignePanierView, PanierView, ZoneLivraisonViewSet

router = DefaultRouter()
router.register('commandes', CommandeViewSet, basename='commande')
router.register('livraison/zones', ZoneLivraisonViewSet, basename='zone-livraison')

urlpatterns = [
    path('panier/', PanierView.as_view(), name='panier'),
    path('panier/lignes/', LignePanierView.as_view(), name='panier-ligne-ajouter'),
    path('panier/lignes/<int:produit_id>/', LignePanierView.as_view(), name='panier-ligne-supprimer'),
    *router.urls,
]
