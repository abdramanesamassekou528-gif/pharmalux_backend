from django.conf import settings
from django.db import models


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255)
    reduction_pourcentage = models.PositiveSmallIntegerField(null=True, blank=True)
    reduction_montant = models.PositiveIntegerField(null=True, blank=True, help_text='FCFA — laisser vide si réduction en %')
    categorie = models.ForeignKey('catalogue.Categorie', null=True, blank=True, on_delete=models.SET_NULL,
                                   help_text="Laisser vide pour un coupon valable sur tout le site")
    montant_minimum = models.PositiveIntegerField(default=0)
    actif = models.BooleanField(default=True)
    expire_le = models.DateField()
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return self.code

    @property
    def reduction_affichee(self):
        if self.reduction_pourcentage:
            return f'{self.reduction_pourcentage}%'
        if self.reduction_montant:
            return f'{self.reduction_montant} FCFA'
        return '—'


class UtilisationCoupon(models.Model):
    """Trace qui a utilisé quel coupon, pour empêcher une réutilisation et
    alimenter « Mes coupons » côté compte client."""
    coupon = models.ForeignKey(Coupon, related_name='utilisations', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coupons_utilises', on_delete=models.CASCADE)
    commande = models.ForeignKey('commandes.Commande', null=True, on_delete=models.SET_NULL)
    utilise_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'utilisateur')
