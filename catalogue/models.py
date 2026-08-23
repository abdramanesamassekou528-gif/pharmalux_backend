from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Categorie(models.Model):
    COULEURS = [
        ('sauge', 'Sauge'), ('corail', 'Corail'), ('lavande', 'Lavande'), ('ciel', 'Ciel'),
    ]
    slug = models.SlugField(unique=True)
    nom = models.CharField(max_length=100)
    icone = models.CharField(max_length=50, help_text="Nom d'icône lucide-react, ex: baby")
    couleur = models.CharField(max_length=20, choices=COULEURS, default='sauge')
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


class SousCategorie(models.Model):
    categorie = models.ForeignKey(Categorie, related_name='sous_categories', on_delete=models.CASCADE)
    slug = models.SlugField()
    nom = models.CharField(max_length=100)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        unique_together = ('categorie', 'slug')
        verbose_name = 'Sous-catégorie'
        verbose_name_plural = 'Sous-catégories'

    def __str__(self):
        return f'{self.categorie.nom} / {self.nom}'


class Marque(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'Marque'
        verbose_name_plural = 'Marques'

    def __str__(self):
        return self.nom


class Produit(models.Model):
    slug = models.SlugField(unique=True)
    nom = models.CharField(max_length=200)
    marque = models.ForeignKey(Marque, related_name='produits', on_delete=models.PROTECT)
    categorie = models.ForeignKey(Categorie, related_name='produits', on_delete=models.PROTECT)
    sous_categorie = models.ForeignKey(SousCategorie, related_name='produits', null=True, blank=True, on_delete=models.SET_NULL)

    prix = models.PositiveIntegerField(help_text='FCFA, sans décimales')
    ancien_prix = models.PositiveIntegerField(null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)
    seuil_stock_faible = models.PositiveIntegerField(default=5)
    sku = models.CharField('Référence (SKU)', max_length=50, unique=True)

    contenance = models.CharField(max_length=50, blank=True)
    poids = models.CharField(max_length=50, blank=True)
    age_recommande = models.CharField(max_length=100, blank=True)

    description = models.TextField()
    composition = models.TextField(blank=True)
    mode_utilisation = models.TextField(blank=True)
    precautions = models.TextField(blank=True)

    # Traçabilité — important pour une parapharmacie (voir section 22 du cahier des charges)
    lot = models.CharField(max_length=50, blank=True)
    date_fabrication = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)

    est_nouveaute = models.BooleanField('Nouveauté', default=False)
    est_bestseller = models.BooleanField('Best-seller', default=False)
    actif = models.BooleanField('Publié', default=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-cree_le']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return f'{self.nom} ({self.sku})'

    @property
    def reduction_pourcentage(self):
        if self.ancien_prix and self.ancien_prix > self.prix:
            return round((1 - self.prix / self.ancien_prix) * 100)
        return 0

    @property
    def en_stock_faible(self):
        return 0 < self.stock <= self.seuil_stock_faible

    @property
    def en_rupture(self):
        return self.stock == 0

    @property
    def tags(self):
        tags = []
        if self.est_nouveaute:
            tags.append('nouveaute')
        if self.reduction_pourcentage > 0:
            tags.append('promo')
        if self.est_bestseller:
            tags.append('bestseller')
        return tags


class ProduitImage(models.Model):
    produit = models.ForeignKey(Produit, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='produits/')
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f'Image #{self.ordre} — {self.produit.nom}'
