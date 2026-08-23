from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AdresseViewSet, ConnexionView, InscriptionView, MoiView

router = DefaultRouter()
router.register('adresses', AdresseViewSet, basename='adresse')

urlpatterns = [
    path('auth/login/', ConnexionView.as_view(), name='auth-login'),
    path('auth/register/', InscriptionView.as_view(), name='auth-register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MoiView.as_view(), name='auth-me'),
    *router.urls,
]
