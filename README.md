# Bébé & Cie — API (Django + PostgreSQL)

Backend de la boutique en ligne, construit avec Django REST Framework et
PostgreSQL. Il implémente exactement le contrat d'API attendu par le
frontend React (`bebe-et-cie-frontend`) : mêmes noms de champs, mêmes formes
de réponse — voir `src/services/api.js` côté frontend pour la fonction
correspondant à chaque endpoint.

Testé de bout en bout pendant le développement : migrations sur PostgreSQL
réel, inscription/connexion, catalogue avec filtres, panier serveur,
checkout complet avec coupon et décrément de stock, avis avec détection
d'achat vérifié, favoris, notifications.

## 1. Installation

Prérequis : Python 3.11+, PostgreSQL 14+.

```bash
python3 -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

Crée la base de données :

```bash
sudo -u postgres psql -c "CREATE DATABASE bebe_cie;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"   # ou l'utilisateur de ton choix
```

Copie `.env.example` en `.env` et adapte les valeurs (au minimum
`DB_PASSWORD` si différent, et un vrai `SECRET_KEY` en production) :

```bash
cp .env.example .env
```

Migrations puis données de démonstration :

```bash
python manage.py migrate
python manage.py creer_roles     # crée les groupes de rôles du back-office
python manage.py seed_data       # recharge les mêmes données que le frontend
python manage.py createsuperuser # ton compte admin
python manage.py runserver
```

L'API est servie sur **http://localhost:8000/api/**, l'admin sur
**http://localhost:8000/admin/**.

Utilisateur de démonstration créé par `seed_data` :
`abdramane@example.ml` / `motdepasse123`.

## 2. Brancher le frontend React dessus

Dans le projet frontend, crée un fichier `.env` avec :

```
VITE_API_URL=http://localhost:8000/api
```

Puis remplace, dans `src/services/api.js`, le corps de chaque fonction par
un `fetch()` vers l'endpoint correspondant (table complète plus bas) — les
noms de champs renvoyés par l'API sont volontairement identiques à ceux de
`mockData.js`, donc **aucun composant React n'a besoin d'être modifié**.

Le CORS est déjà configuré pour `http://localhost:5173` (le serveur Vite par
défaut) dans `.env` / `CORS_ALLOWED_ORIGINS`.

## 3. Structure du projet

```
config/          Réglages Django (settings, urls racine)
comptes/          Utilisateur custom (email = identifiant), adresses, JWT
catalogue/        Catégories, sous-catégories, marques, produits, images
avis/             Avis produits (achat vérifié calculé automatiquement)
commandes/        Panier serveur, commandes, lignes, paiement, historique
                  de statut, zones de livraison
promotions/       Coupons + suivi d'utilisation par utilisateur
notifications/    Notifications (commande, promo, stock, panier abandonné)
favoris/          Liste de favoris par utilisateur
```

Chaque app suit le même schéma : `models.py`, `serializers.py`, `views.py`,
`urls.py`, `admin.py`.

## 4. Endpoints

| Endpoint | Méthode(s) | Auth | Description |
|---|---|---|---|
| `/api/auth/register/` | POST | non | Inscription — renvoie `{access, refresh, user}` |
| `/api/auth/login/` | POST | non | Connexion `{email, password}` — renvoie `{access, refresh, user}` |
| `/api/auth/refresh/` | POST | non | Rafraîchit le token d'accès |
| `/api/auth/me/` | GET, PATCH | oui | Profil de l'utilisateur connecté |
| `/api/categories/` | GET | non | Arborescence catégories/sous-catégories |
| `/api/marques/` | GET | non | Liste des marques |
| `/api/produits/` | GET | non | Liste, filtrable : `categorie`, `sous_categorie`, `marque`, `prix_max`, `en_stock`, `promo`, `nouveaute`, `bestseller`, `search`, `tri` (`prix_asc`/`prix_desc`/`note`/`populaire`/`nouveaute`) |
| `/api/produits/{slug}/` | GET | non | Fiche produit complète |
| `/api/produits/{slug}/similaires/` | GET | non | Produits similaires |
| `/api/avis/?produit={slug}` | GET | non | Avis d'un produit |
| `/api/avis/` | POST | oui | Publier un avis `{productId, note, commentaire, photo}` |
| `/api/panier/` | GET | oui | Mon panier serveur |
| `/api/panier/lignes/` | POST | oui | Ajouter/mettre à jour une ligne `{productId, quantite}` |
| `/api/panier/lignes/{produit_id}/` | DELETE | oui | Retirer une ligne |
| `/api/commandes/` | GET | oui | Mes commandes |
| `/api/commandes/` | POST | oui | Passer commande à partir du panier serveur `{zone, adresse_detail, mode_livraison, methode_paiement, code_coupon}` |
| `/api/commandes/{reference}/` | GET | oui | Détail + timeline de suivi |
| `/api/commandes/{reference}/avancer/` | POST | staff | Fait avancer le statut (back-office) |
| `/api/livraison/zones/` | GET | non | Zones de livraison et tarifs |
| `/api/coupons/` | GET | oui | Coupons actifs, avec `utilise` pour l'utilisateur connecté |
| `/api/coupons/appliquer/` | POST | oui | Valide un code `{code}` |
| `/api/notifications/` | GET | oui | Mes notifications |
| `/api/notifications/{id}/marquer_lu/` | POST | oui | Marquer comme lue |
| `/api/favoris/` | GET, POST | oui | Mes favoris / en ajouter `{productId}` |
| `/api/favoris/{id}/` | DELETE | oui | Retirer un favori |
| `/api/adresses/` | GET, POST | oui | Mes adresses |
| `/api/adresses/{id}/` | PATCH, DELETE | oui | Modifier/supprimer une adresse |

Toutes les listes sont paginées (12 par page) sauf mention contraire.
Authentification par JWT : header `Authorization: Bearer <access>`.

## 5. Le back-office, presque gratuit

L'admin Django (`/admin/`) est personnalisé pour couvrir une bonne partie des
sections 20 à 28 du cahier des charges sans code front-end supplémentaire :

- **Produits** : indicateur visuel stock faible / rupture, indicateur
  péremption proche (J-60) ou dépassée, actions groupées (marquer
  best-seller/nouveauté).
- **Commandes** : badge de statut coloré, articles/paiement/historique en
  ligne, actions groupées pour faire avancer le statut (« → Préparation »,
  « → Expédition »...) qui alimentent automatiquement la timeline consommée
  par le frontend.
- **Utilisateurs & rôles** : `python manage.py creer_roles` crée les groupes
  `ADMIN`, `GESTIONNAIRE_STOCK`, `VENDEUR`, `COMPTABLE`, `LIVREUR`,
  `SERVICE_CLIENT` avec des permissions Django adaptées à chacun (le rôle
  `SUPER_ADMIN` du cahier des charges correspond à `is_superuser=True`).
- **Coupons, avis, notifications** : gérables directement depuis l'admin.

Pour un vrai tableau de bord visuel (graphiques de ventes, statistiques —
sections 25 et 28), il vaudra mieux construire une interface React dédiée
qui consomme ces mêmes modèles via de nouveaux endpoints `GET` en lecture
seule (agrégations avec `annotate`/`aggregate`) plutôt que d'alourdir
l'admin Django.

## 6. Ce qui n'est pas couvert (et pistes pour la suite)

- **Paiement mobile réel** (Orange Money, Moov Money, Wave) : le modèle
  `Paiement` et le flux de checkout sont prêts à recevoir un webhook de
  confirmation, mais l'intégration avec chaque opérateur (signature des
  requêtes, redirections, USSD...) est spécifique à chaque prestataire et
  évolue régulièrement — à implémenter en consultant leur documentation
  officielle au moment venu.
- **Panier abandonné** (emails/SMS de relance) : nécessite une tâche
  planifiée (Celery + Celery Beat, ou une simple commande cron) qui
  parcourt les paniers non modifiés depuis X heures.
- **Recherche/tri par pertinence textuelle avancée** : le champ `search`
  utilise `icontains` (sensible aux accents). Pour une recherche plus
  tolérante, envisager l'extension PostgreSQL `unaccent` ou `pg_trgm`.
- **Statistiques/rapports, fidélité, parrainage, géolocalisation, IA** :
  hors scope de cette itération (comme pour le frontend), mais les modèles
  existants (commandes, avis, utilisateurs) donnent une bonne base pour les
  construire ensuite.

## 7. Commandes utiles

```bash
python manage.py migrate              # appliquer les migrations
python manage.py seed_data            # (re)charger les données de démo
python manage.py creer_roles          # créer les groupes de rôles
python manage.py createsuperuser      # créer un compte admin
python manage.py runserver            # lancer le serveur de dev
python manage.py test                 # lancer les tests (squelettes à compléter)
```
