from rest_framework import viewsets, permissions
from .models import Avis
from .serializers import AvisSerializer


class EstProprietaireOuLectureSeule(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.utilisateur == request.user


class AvisViewSet(viewsets.ModelViewSet):
    """
    GET  /api/avis/?produit=<slug>    avis d'un produit (public)
    POST /api/avis/                   publier un avis (authentifié)
    """
    serializer_class = AvisSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, EstProprietaireOuLectureSeule]

    def get_queryset(self):
        qs = Avis.objects.select_related('utilisateur', 'produit').filter(signale=False)
        produit_slug = self.request.query_params.get('produit')
        if produit_slug:
            qs = qs.filter(produit__slug=produit_slug)
        utilisateur_id = self.request.query_params.get('mes_avis')
        if utilisateur_id and self.request.user.is_authenticated:
            qs = qs.filter(utilisateur=self.request.user)
        return qs
