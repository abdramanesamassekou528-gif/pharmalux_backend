from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    """
    Utilisateur custom : on garde first_name/last_name/email de Django
    (exposés côté API comme prenom/nom pour coller au frontend) et on
    ajoute le téléphone, utile pour la livraison et les paiements mobiles.
    Les rôles (SUPER_ADMIN, ADMIN, GESTIONNAIRE_STOCK, VENDEUR, COMPTABLE,
    LIVREUR, SERVICE_CLIENT) sont gérés via les Groups Django standard —
    voir `comptes/management/commands/creer_roles.py`.
    """
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Adresse(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, related_name='adresses', on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    ville = models.CharField(max_length=100, default='Bamako')
    commune = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    details = models.CharField(max_length=255, blank=True)
    par_defaut = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-par_defaut', '-cree_le']

    def __str__(self):
        return f'{self.label} — {self.commune}, {self.ville}'

    def save(self, *args, **kwargs):
        # Une seule adresse par défaut par utilisateur.
        if self.par_defaut:
            Adresse.objects.filter(utilisateur=self.utilisateur, par_defaut=True).exclude(pk=self.pk).update(par_defaut=False)
        super().save(*args, **kwargs)
