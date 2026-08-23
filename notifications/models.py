from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPES = [
        ('commande', 'Commande'),
        ('promotion', 'Promotion'),
        ('stock', 'Stock'),
        ('panier_abandonne', 'Panier abandonné'),
    ]
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=TYPES)
    titre = models.CharField(max_length=150)
    message = models.CharField(max_length=255)
    lu = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-cree_le']

    def __str__(self):
        return self.titre
