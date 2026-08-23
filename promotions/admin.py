from django.contrib import admin
from .models import Coupon, UtilisationCoupon


class UtilisationCouponInline(admin.TabularInline):
    model = UtilisationCoupon
    extra = 0
    readonly_fields = ['utilisateur', 'commande', 'utilise_le']
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'reduction_affichee', 'categorie', 'expire_le', 'actif']
    list_filter = ['actif', 'categorie']
    search_fields = ['code']
    inlines = [UtilisationCouponInline]
