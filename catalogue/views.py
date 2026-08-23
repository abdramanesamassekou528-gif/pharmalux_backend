from django.db.models import Avg, Count, Q
from rest_framework import viewsets, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import ProduitFilter
from .models import Categorie, Marque, Produit
from .serializers import CategorieSerializer, MarqueSerializer, ProduitDetailSerializer, ProduitListSerializer


def annoter_produits(queryset):
    return queryset.select_related('marque', 'categorie', 'sous_categorie').prefetch_related('images').annotate(
        note_moyenne=Avg('avis__note'),
        avis_count=Count('avis', distinct=True),
    )


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.prefetch_related('sous_categories').all()
    serializer_class = CategorieSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class MarqueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Marque.objects.all()
    serializer_class = MarqueSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ProduitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/produits/                         liste + filtres + tri + recherche
    GET /api/produits/{slug}/                   fiche produit complète
    GET /api/produits/{slug}/similaires/        produits similaires (même catégorie/marque)
    GET /api/produits/{slug}/avis/              avis du produit (voir avis.views aussi via router imbriqué)
    """
    queryset = annoter_produits(Produit.objects.filter(actif=True))
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    filterset_class = ProduitFilter
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter, ]
    search_fields = ['nom', 'marque__nom', 'categorie__nom', 'sku']
    ordering_fields = ['prix', 'note_moyenne', 'avis_count', 'cree_le']

    def get_queryset(self):
        from django_filters.rest_framework import DjangoFilterBackend
        qs = super().get_queryset()
        qs = DjangoFilterBackend().filter_queryset(self.request, qs, self)
        tri = self.request.query_params.get('tri')
        if tri == 'prix_asc':
            qs = qs.order_by('prix')
        elif tri == 'prix_desc':
            qs = qs.order_by('-prix')
        elif tri == 'note':
            qs = qs.order_by('-note_moyenne')
        elif tri == 'populaire':
            qs = qs.order_by('-avis_count')
        elif tri == 'nouveaute':
            qs = qs.order_by('-est_nouveaute', '-cree_le')
        return qs

    def get_serializer_class(self):
        return ProduitDetailSerializer if self.action == 'retrieve' else ProduitListSerializer

    @action(detail=True, methods=['get'])
    def similaires(self, request, slug=None):
        produit = self.get_object()
        qs = annoter_produits(Produit.objects.filter(actif=True).exclude(id=produit.id).filter(
            Q(categorie=produit.categorie) | Q(marque=produit.marque)
        ))[:4]
        serializer = ProduitListSerializer(qs, many=True)
        return Response(serializer.data)
