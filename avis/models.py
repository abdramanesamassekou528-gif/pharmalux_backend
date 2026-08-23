from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings


class Avis(models.Model):
    produit = models.ForeignKey('catalogue.Produit', related_name='avis', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='avis', on_delete=models.CASCADE)
    note = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    photo = models.ImageField(upload_to='avis/', null=True, blank=True)
    # Vrai si l'utilisateur a une commande livrée contenant ce produit (calculé à la création).
    verifie = models.BooleanField(default=False)
    signale = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']
        unique_together = ('produit', 'utilisateur')
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'

    def __str__(self):
        return f'{self.note}\u2605 {self.produit.nom} par {self.utilisateur}'
