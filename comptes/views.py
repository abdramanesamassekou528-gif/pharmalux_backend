from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Adresse
from .serializers import AdresseSerializer, InscriptionSerializer, UtilisateurSerializer


def jetons_pour(utilisateur):
    refresh = RefreshToken.for_user(utilisateur)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


class ConnexionSerializer(TokenObtainPairSerializer):
    """Ajoute le profil utilisateur dans la réponse de connexion, pour que le
    frontend obtienne directement { access, refresh, user } comme avec le
    `loginUser` mock actuel."""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UtilisateurSerializer(self.user).data
        return data


class ConnexionView(TokenObtainPairView):
    """POST /api/auth/login/ avec { email, password }"""
    serializer_class = ConnexionSerializer


class InscriptionView(generics.CreateAPIView):
    """POST /api/auth/register/ — crée le compte et renvoie directement les tokens + le profil,
    pour matcher ce que le frontend attend de `registerUser`."""
    permission_classes = [permissions.AllowAny]
    serializer_class = InscriptionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        utilisateur = serializer.save()
        data = {**jetons_pour(utilisateur), 'user': UtilisateurSerializer(utilisateur).data}
        return Response(data, status=201)


class MoiView(APIView):
    """GET /api/auth/me/ — profil de l'utilisateur connecté."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UtilisateurSerializer(request.user).data)

    def patch(self, request):
        serializer = UtilisateurSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdresseViewSet(viewsets.ModelViewSet):
    serializer_class = AdresseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Adresse.objects.filter(utilisateur=self.request.user)
