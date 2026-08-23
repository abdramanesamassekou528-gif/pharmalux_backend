from rest_framework.routers import DefaultRouter
from .views import CategorieViewSet, MarqueViewSet, ProduitViewSet

router = DefaultRouter()
router.register('categories', CategorieViewSet, basename='categorie')
router.register('marques', MarqueViewSet, basename='marque')
router.register('produits', ProduitViewSet, basename='produit')

urlpatterns = router.urls
