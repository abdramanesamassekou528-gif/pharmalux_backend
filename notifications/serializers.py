from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='cree_le', format='%Y-%m-%d %H:%M', read_only=True)
    titre = serializers.CharField()
    lu = serializers.BooleanField()

    class Meta:
        model = Notification
        fields = ['id', 'type', 'titre', 'message', 'date', 'lu']
