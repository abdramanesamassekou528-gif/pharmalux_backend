from django.urls import path
from .views import AppliquerCouponView, CouponListeView

urlpatterns = [
    path('coupons/', CouponListeView.as_view(), name='coupons-liste'),
    path('coupons/appliquer/', AppliquerCouponView.as_view(), name='coupons-appliquer'),
]
