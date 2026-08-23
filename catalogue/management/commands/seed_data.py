from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from catalogue.models import Categorie, SousCategorie, Marque, Produit
from commandes.models import ZoneLivraison, Commande, LigneCommande, HistoriqueCommande, Paiement
from promotions.models import Coupon
from notifications.models import Notification
from avis.models import Avis
from favoris.models import Favori
from comptes.models import Adresse

Utilisateur = get_user_model()

CATEGORIES = [
    {'slug': 'bebe', 'nom': 'Bébé', 'icone': 'baby', 'couleur': 'corail', 'sous': [
        ('alimentation', 'Alimentation bébé'), ('hygiene-bebe', 'Hygiène bébé'), ('sommeil', 'Sommeil'),
        ('sortie', 'Sortie'), ('securite', 'Sécurité'), ('vetements', 'Vêtements'),
    ]},
    {'slug': 'maman', 'nom': 'Maman', 'icone': 'heart-handshake', 'couleur': 'lavande', 'sous': [
        ('grossesse', 'Grossesse'), ('allaitement', 'Allaitement'), ('post-partum', 'Après grossesse'),
    ]},
    {'slug': 'hygiene', 'nom': 'Hygiène', 'icone': 'droplets', 'couleur': 'ciel', 'sous': [
        ('hygiene-corporelle', 'Hygiène corporelle'), ('hygiene-bucco-dentaire', 'Hygiène bucco-dentaire'),
        ('hygiene-intime', 'Hygiène intime'), ('desinfection', 'Désinfection'),
    ]},
    {'slug': 'beaute', 'nom': 'Beauté', 'icone': 'sparkles', 'couleur': 'corail', 'sous': [
        ('visage', 'Visage'), ('corps', 'Corps'), ('cheveux', 'Cheveux'), ('solaires', 'Solaires'),
    ]},
    {'slug': 'soins', 'nom': 'Soins', 'icone': 'stethoscope', 'couleur': 'sauge', 'sous': [
        ('peau', 'Peau'), ('cheveux-soins', 'Cheveux'), ('pieds', 'Pieds'), ('mains', 'Mains'),
    ]},
]

BRANDS = ['Mustela', 'Klorane Bébé', 'Bioderma', 'Avène', 'A-Derma', 'La Roche-Posay', 'Weleda', 'Nuk', 'Chicco', 'Neno']

# (slug, nom, marque, categorie, sous_categorie, prix, ancien_prix, stock, sku, contenance, poids, age, desc, nouveaute, bestseller, lot_jours_avant_expiration)
PRODUITS = [
    ('mustela-creme-hydratante-bebe', 'Crème Hydratante Bébé', 'Mustela', 'bebe', 'hygiene-bebe', 6500, 7500, 24, 'MUS-CRH-100', '200 ml', '210 g', 'Dès la naissance',
     "Crème corps quotidienne qui hydrate intensément la peau fragile de bébé pendant 24h.", False, True, 700),
    ('klorane-shampoing-camomille', 'Shampoing Douceur à la Camomille', 'Klorane Bébé', 'bebe', 'hygiene-bebe', 5200, None, 18, 'KLO-SHC-200', '200 ml', '215 g', 'Dès la naissance',
     "Shampoing sans larmes qui nettoie tout en douceur le cuir chevelu de bébé.", True, False, 730),
    ('nuk-biberon-first-choice', 'Biberon First Choice+ 260ml', 'Nuk', 'bebe', 'alimentation', 8900, 10500, 12, 'NUK-BIB-260', '260 ml', '95 g', '0-6 mois',
     "Biberon anti-colique avec tétine en silicone qui imite la forme du sein maternel.", False, False, None),
    ('chicco-poussette-urban', 'Poussette Urban Plus', 'Chicco', 'bebe', 'sortie', 145000, 165000, 4, 'CHI-POU-URB', None, '9.8 kg', '0-36 mois',
     "Poussette compacte, pliage une main, panier XL et canopy anti-UV.", False, True, None),
    ('mustela-liniment-oleo-calcaire', 'Liniment Oléo-Calcaire', 'Mustela', 'bebe', 'hygiene-bebe', 4200, None, 3, 'MUS-LIN-500', '500 ml', '520 g', 'Dès la naissance',
     "Nettoie et protège la peau du siège de bébé à chaque change.", False, False, 120),
    ('gigoteuse-hiver-etoiles', 'Gigoteuse Hiver Étoiles TOG 2.5', 'Neno', 'bebe', 'sommeil', 12500, None, 15, 'NEN-GIG-090', 'Taille 6-18 mois', '340 g', '6-18 mois',
     "Gigoteuse chaude en coton biologique, ouverture zip intégral.", True, False, None),
    ('weleda-huile-massage-grossesse', 'Huile de Massage Grossesse', 'Weleda', 'maman', 'grossesse', 9800, None, 21, 'WEL-HMG-100', '100 ml', '120 g', 'Adulte',
     "Prévient l'apparition des vergetures, maintient l'élasticité de la peau.", False, True, 700),
    ('coussinets-allaitement-nuk', "Coussinets d'Allaitement Ultra Absorbants", 'Nuk', 'maman', 'allaitement', 4500, 5200, 40, 'NUK-COU-036', '36 pièces', '90 g', 'Adulte',
     "Coussinets ultra-fins et respirants, absorbent les fuites de lait.", False, False, None),
    ('ceinture-post-partum', 'Ceinture de Soutien Post-Partum', 'Chicco', 'maman', 'post-partum', 15900, None, 9, 'CHI-CPP-M', 'Taille M/L', '180 g', 'Adulte',
     "Soutient le dos et l'abdomen après l'accouchement.", False, False, None),
    ('bioderma-atoderm-gel-douche', 'Atoderm Gel Douche Surgras', 'Bioderma', 'hygiene', 'hygiene-corporelle', 7200, None, 55, 'BIO-ATD-500', '500 ml', '520 g', 'Toute la famille',
     "Gel douche surgras pour peaux sèches, respecte le film hydrolipidique.", False, True, 700),
    ('avene-eau-thermale', 'Eau Thermale Spray', 'Avène', 'soins', 'peau', 5900, 6800, 60, 'AVE-EAU-300', '300 ml', '340 g', 'Toute la famille',
     "Eau thermale apaisante qui calme les tiraillements et rafraîchit la peau.", False, True, 800),
    ('la-roche-posay-anthelios', 'Anthelios SPF50+ Fluide Bébé', 'La Roche-Posay', 'beaute', 'solaires', 11500, None, 6, 'LRP-ANT-050', '50 ml', '65 g', 'Dès 6 mois',
     "Protection solaire très haute résistance pour la peau fragile de bébé.", True, False, 700),
    ('aderma-exomega-baume', 'Exomega Control Baume Émollient', 'A-Derma', 'soins', 'peau', 9200, 10800, 8, 'ADE-EXO-400', '400 ml', '430 g', 'Dès la naissance',
     "Baume émollient qui nourrit intensément les peaux atopiques.", False, False, 45),
    ('chauffe-biberon-nuk', 'Chauffe-Biberon Express', 'Nuk', 'bebe', 'alimentation', 18500, None, 11, 'NUK-CHB-01', None, '650 g', '0-36 mois',
     "Chauffe le lait et les petits pots en quelques minutes.", False, False, None),
    ('sterilisateur-vapeur-chicco', 'Stérilisateur Vapeur 6 Biberons', 'Chicco', 'bebe', 'alimentation', 32000, 36000, 5, 'CHI-STE-06', None, '1.1 kg', '0-24 mois',
     "Stérilise jusqu'à 6 biberons en 8 minutes à la vapeur.", False, False, None),
    ('couches-taille-4', 'Couches Douceur Taille 4 (9-14kg)', 'Nuk', 'bebe', 'hygiene-bebe', 8500, None, 2, 'NUK-COU-T4', '44 couches', '1.4 kg', '9-14 kg',
     "Couches ultra-absorbantes jusqu'à 12h, indicateur d'humidité.", False, True, 1000),
    ('lingettes-eau-nuk', "Lingettes à l'Eau x80", 'Nuk', 'bebe', 'hygiene-bebe', 3200, 3800, 70, 'NUK-LIN-080', '80 lingettes', '480 g', 'Dès la naissance',
     "Lingettes composées à 99% d'eau, sans savon ni alcool.", False, False, 700),
    ('tire-lait-electrique', 'Tire-Lait Électrique Double Pompage', 'Nuk', 'maman', 'allaitement', 52000, 59000, 3, 'NUK-TL-DP', None, '780 g', 'Adulte',
     "Tire-lait électrique silencieux, 8 niveaux d'aspiration, double pompage.", False, False, None),
]

ZONES = [
    ('Commune I', 1000, '24h'), ('Commune II', 1000, '24h'), ('Commune III', 1000, '24h'),
    ('Commune IV', 1500, '24-48h'), ('Commune V', 1500, '24-48h'), ('Commune VI', 1500, '24-48h'),
    ('Autres régions (Sikasso, Ségou...)', 3500, '3-5 jours'),
]

COUPONS = [
    ('BIENVENUE10', "10% sur votre première commande", 10, None, 30),
    ('BEBE15', "15% sur tout le rayon Bébé", 15, None, 15),
    ('MAMAN2026', "2 000 FCFA de réduction dès 20 000 FCFA", None, 2000, -30),
]


class Command(BaseCommand):
    help = "Charge un jeu de données de démonstration identique à celui du frontend React (mockData.js)."

    def handle(self, *args, **options):
        today = date.today()

        self.stdout.write('Catégories…')
        categorie_par_slug, sous_par_slug = {}, {}
        for i, c in enumerate(CATEGORIES):
            cat, _ = Categorie.objects.update_or_create(
                slug=c['slug'], defaults={'nom': c['nom'], 'icone': c['icone'], 'couleur': c['couleur'], 'ordre': i}
            )
            categorie_par_slug[c['slug']] = cat
            for j, (sslug, snom) in enumerate(c['sous']):
                sc, _ = SousCategorie.objects.update_or_create(
                    categorie=cat, slug=sslug, defaults={'nom': snom, 'ordre': j}
                )
                sous_par_slug[sslug] = sc

        self.stdout.write('Marques…')
        marque_par_nom = {nom: Marque.objects.get_or_create(nom=nom)[0] for nom in BRANDS}

        self.stdout.write('Produits…')
        produits_par_slug = {}
        for (slug, nom, marque, cat_slug, sous_slug, prix, ancien_prix, stock, sku, contenance, poids, age,
             desc, nouveaute, bestseller, jours_expiration) in PRODUITS:
            expiration = today + timedelta(days=jours_expiration) if jours_expiration else None
            fabrication = today - timedelta(days=90) if jours_expiration else None
            produit, _ = Produit.objects.update_or_create(
                slug=slug,
                defaults=dict(
                    nom=nom, marque=marque_par_nom[marque], categorie=categorie_par_slug[cat_slug],
                    sous_categorie=sous_par_slug.get(sous_slug), prix=prix, ancien_prix=ancien_prix,
                    stock=stock, sku=sku, contenance=contenance or '', poids=poids or '', age_recommande=age or '',
                    description=desc, composition="Formule douce, sans parabène, testée sous contrôle dermatologique.",
                    mode_utilisation="Voir la notice fournie avec le produit pour un usage optimal.",
                    precautions="Usage externe. Ne pas utiliser sur une peau lésée sans avis médical.",
                    lot=f'{sku[:3]}{stock:03d}' if jours_expiration else '', date_fabrication=fabrication,
                    date_expiration=expiration, est_nouveaute=nouveaute, est_bestseller=bestseller,
                )
            )
            produits_par_slug[slug] = produit

        self.stdout.write('Zones de livraison…')
        for i, (commune, prix, delai) in enumerate(ZONES):
            ZoneLivraison.objects.update_or_create(commune=commune, defaults={'prix': prix, 'delai': delai, 'ordre': i})

        self.stdout.write('Coupons…')
        for code, desc, pct, montant, jours in COUPONS:
            Coupon.objects.update_or_create(code=code, defaults={
                'description': desc, 'reduction_pourcentage': pct, 'reduction_montant': montant,
                'expire_le': today + timedelta(days=jours),
            })

        self.stdout.write('Utilisateur de démonstration…')
        demo, cree = Utilisateur.objects.get_or_create(
            email='abdramane@example.ml',
            defaults={'username': 'abdramane@example.ml', 'first_name': 'Abdramane', 'last_name': 'Traoré', 'telephone': '+223 76 00 00 00'},
        )
        if cree:
            demo.set_password('motdepasse123')
            demo.save()

        Adresse.objects.get_or_create(utilisateur=demo, label='Domicile', defaults={
            'ville': 'Bamako', 'commune': 'Commune III', 'quartier': 'Hippodrome', 'details': 'Rue 234, Porte 12', 'par_defaut': True,
        })
        Adresse.objects.get_or_create(utilisateur=demo, label='Bureau', defaults={
            'ville': 'Bamako', 'commune': 'Commune II', 'quartier': 'Quinzambougou', 'details': 'Immeuble Diarra, 2e étage',
        })

        self.stdout.write('Avis…')
        avis_demo = [
            ('mustela-creme-hydratante-bebe', 5, True, "Ma fille a la peau très sensible et cette crème ne l'a jamais irritée."),
            ('weleda-huile-massage-grossesse', 5, True, "Aucune vergeture apparue depuis le 4ème mois, odeur agréable."),
            ('bioderma-atoderm-gel-douche', 5, True, "Toute la famille l'utilise, même les enfants eczémateux le supportent bien."),
            ('avene-eau-thermale', 5, True, "Indispensable dans la salle de bain, apaise immédiatement."),
        ]
        for slug, note, verifie, commentaire in avis_demo:
            Avis.objects.get_or_create(produit=produits_par_slug[slug], utilisateur=demo, defaults={
                'note': note, 'verifie': verifie, 'commentaire': commentaire,
            })

        Favori.objects.get_or_create(utilisateur=demo, produit=produits_par_slug['mustela-creme-hydratante-bebe'])
        Favori.objects.get_or_create(utilisateur=demo, produit=produits_par_slug['weleda-huile-massage-grossesse'])

        self.stdout.write('Commande de démonstration…')
        if not Commande.objects.filter(utilisateur=demo).exists():
            commande = Commande.objects.create(
                utilisateur=demo, statut='en_livraison',
                adresse_texte='Bamako, Commune III, Hippodrome', mode_livraison='standard',
                frais_livraison=1000, sous_total=16900, reduction=0, total=17900,
            )
            for etape in ['commande_confirmee', 'paiement_confirme', 'preparation', 'expedition', 'en_livraison']:
                HistoriqueCommande.objects.create(commande=commande, etape=etape)
            LigneCommande.objects.create(commande=commande, produit=produits_par_slug['mustela-creme-hydratante-bebe'], quantite=1, prix_unitaire=6500)
            LigneCommande.objects.create(commande=commande, produit=produits_par_slug['bioderma-atoderm-gel-douche'], quantite=1, prix_unitaire=7200)
            LigneCommande.objects.create(commande=commande, produit=produits_par_slug['lingettes-eau-nuk'], quantite=2, prix_unitaire=3200)
            Paiement.objects.create(commande=commande, methode='orange_money', statut='reussi', montant=17900)

        self.stdout.write('Notifications…')
        Notification.objects.get_or_create(utilisateur=demo, type='commande', titre='Commande en cours de livraison', defaults={
            'message': 'Votre commande arrive aujourd\u2019hui.',
        })
        Notification.objects.get_or_create(utilisateur=demo, type='promotion', titre='Promotion Bébé', defaults={
            'message': '-15% sur tout le rayon bébé jusqu\u2019au 30 août.', 'lu': True,
        })

        self.stdout.write(self.style.SUCCESS(
            f'Terminé : {len(PRODUITS)} produits, {len(CATEGORIES)} catégories, {len(BRANDS)} marques, '
            f'{len(ZONES)} zones, {len(COUPONS)} coupons. Utilisateur démo : abdramane@example.ml / motdepasse123'
        ))
