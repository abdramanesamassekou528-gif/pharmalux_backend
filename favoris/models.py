from django.conf import settings
from django.db import models


class Favori(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='favoris', on_delete=models.CASCADE)
    produit = models.ForeignKey('catalogue.Produit', related_name='favorise_par', on_delete=models.CASCADE)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']
        unique_together = ('utilisateur', 'produit')

    def __str__(self):
        return f'{self.utilisateur} \u2665 {self.produit.nom}'
