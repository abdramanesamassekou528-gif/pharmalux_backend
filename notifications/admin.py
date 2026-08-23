from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'utilisateur', 'type', 'lu', 'cree_le']
    list_filter = ['type', 'lu']
    search_fields = ['titre', 'utilisateur__email']
