import random
from django.conf import settings
from django.db import models
from django.utils import timezone


class ZoneLivraison(models.Model):
    commune = models.CharField(max_length=100, unique=True)
    prix = models.PositiveIntegerField()
    delai = models.CharField(max_length=50, help_text='ex: 24h, 24-48h, 3-5 jours')
    ordre = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['ordre', 'commune']
        verbose_name = 'Zone de livraison'
        verbose_name_plural = 'Zones de livraison'

    def __str__(self):
        return f'{self.commune} — {self.prix} FCFA ({self.delai})'


class Panier(models.Model):
    """Panier serveur, pour le bouton « Enregistrer le panier » côté frontend
    et pour retrouver son panier sur un autre appareil."""
    utilisateur = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='panier', on_delete=models.CASCADE)
    maj_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Panier de {self.utilisateur}'


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='lignes', on_delete=models.CASCADE)
    produit = models.ForeignKey('catalogue.Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('panier', 'produit')


def generer_reference():
    annee = timezone.now().year
    return f'CMD-{annee}-{random.randint(10000, 99999)}'


class Commande(models.Model):
    STATUTS = [
        ('commande_confirmee', 'Commande confirmée'),
        ('paiement_confirme', 'Paiement confirmé'),
        ('preparation', 'Préparation'),
        ('expedition', 'Expédition'),
        ('en_livraison', 'En livraison'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    MODES_LIVRAISON = [
        ('standard', 'Livraison standard'),
        ('express', 'Livraison express'),
        ('retrait', 'Retrait en magasin'),
    ]

    reference = models.CharField(max_length=20, unique=True, default=generer_reference)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='commandes', on_delete=models.CASCADE)
    statut = models.CharField(max_length=30, choices=STATUTS, default='commande_confirmee')

    adresse_texte = models.CharField(max_length=255)
    mode_livraison = models.CharField(max_length=20, choices=MODES_LIVRAISON, default='standard')
    frais_livraison = models.PositiveIntegerField(default=0)

    coupon = models.ForeignKey('promotions.Coupon', null=True, blank=True, on_delete=models.SET_NULL)
    sous_total = models.PositiveIntegerField()
    reduction = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField()

    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-cree_le']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'

    def __str__(self):
        return self.reference

    def avancer_statut(self, nouveau_statut):
        """Change le statut et journalise l'étape dans l'historique
        (alimente directement la timeline affichée côté frontend)."""
        self.statut = nouveau_statut
        self.save(update_fields=['statut', 'maj_le'])
        if nouveau_statut != 'annulee':
            HistoriqueCommande.objects.get_or_create(commande=self, etape=nouveau_statut)


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, related_name='articles', on_delete=models.CASCADE)
    produit = models.ForeignKey('catalogue.Produit', on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.PositiveIntegerField(help_text='Prix figé au moment de la commande')

    def __str__(self):
        return f'{self.quantite} × {self.produit.nom}'


class HistoriqueCommande(models.Model):
    """Une ligne par étape atteinte. Les étapes non encore atteintes sont
    simplement absentes — le serializer reconstruit la timeline complète
    (fait=True/False) en comparant à la liste ordonnée des statuts."""
    commande = models.ForeignKey(Commande, related_name='historique', on_delete=models.CASCADE)
    etape = models.CharField(max_length=30, choices=Commande.STATUTS)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        unique_together = ('commande', 'etape')


class Paiement(models.Model):
    METHODES = [
        ('orange_money', 'Orange Money'),
        ('moov_money', 'Moov Money'),
        ('wave', 'Wave'),
        ('carte', 'Carte bancaire'),
        ('livraison', 'Paiement à la livraison'),
    ]
    STATUTS = [
        ('en_attente', 'En attente'),
        ('reussi', 'Réussi'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
        ('annule', 'Annulé'),
    ]
    commande = models.OneToOneField(Commande, related_name='paiement', on_delete=models.CASCADE)
    methode = models.CharField(max_length=30, choices=METHODES)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    montant = models.PositiveIntegerField()
    reference_transaction = models.CharField(max_length=100, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Paiement {self.get_methode_display()} — {self.commande.reference}'
