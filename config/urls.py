from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalogue.urls')),
    path('api/', include('avis.urls')),
    path('api/', include('commandes.urls')),
    path('api/', include('promotions.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('favoris.urls')),
    path('api/', include('comptes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Bébé & Cie — Administration'
admin.site.site_title = 'Bébé & Cie'
admin.site.index_title = 'Tableau de bord'
