from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    reduction = serializers.CharField(source='reduction_affichee', read_only=True)
    expire = serializers.DateField(source='expire_le', format='%Y-%m-%d', read_only=True)
    utilise = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ['code', 'description', 'reduction', 'expire', 'utilise']

    def get_utilise(self, obj):
        utilisateur = self.context['request'].user
        if not utilisateur.is_authenticated:
            return False
        return obj.utilisations.filter(utilisateur=utilisateur).exists()
