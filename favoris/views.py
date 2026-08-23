from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from .models import Favori
from .serializers import FavoriSerializer


class FavoriViewSet(viewsets.ModelViewSet):
    """
    GET    /api/favoris/              mes favoris
    POST   /api/favoris/  {productId} ajouter
    DELETE /api/favoris/{id}/         retirer
    """
    serializer_class = FavoriSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Favori.objects.filter(utilisateur=self.request.user).select_related(
            'produit__marque', 'produit__categorie'
        )

    def create(self, request, *args, **kwargs):
        existant = Favori.objects.filter(utilisateur=request.user, produit_id=request.data.get('productId')).first()
        if existant:
            return Response(FavoriSerializer(existant).data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(utilisateur=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
