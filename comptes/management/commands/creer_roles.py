from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# Reprend les rôles du cahier des charges (section 26 — Gestion des utilisateurs).
# Django gère nativement les permissions par modèle (add/change/delete/view) ;
# on les assigne ici à des groupes nommés comme dans le document.
ROLES = {
    'SUPER_ADMIN': None,  # accès total → is_superuser=True sur l'utilisateur, pas de groupe nécessaire
    'ADMIN': {
        'catalogue': '__all__',
        'commandes': '__all__',
        'comptes': ['view', 'change'],
        'avis': ['view', 'change', 'delete'],
    },
    'GESTIONNAIRE_STOCK': {
        'catalogue': ['view', 'change'],
    },
    'VENDEUR': {
        'catalogue': ['view'],
        'commandes': ['view', 'change'],
    },
    'COMPTABLE': {
        'commandes': ['view'],
        'promotions': ['view'],
    },
    'LIVREUR': {
        'commandes': ['view', 'change'],
    },
    'SERVICE_CLIENT': {
        'commandes': ['view'],
        'avis': ['view', 'change'],
        'notifications': ['view', 'add', 'change'],
    },
}


class Command(BaseCommand):
    help = "Crée les groupes de rôles du back-office (SUPER_ADMIN, ADMIN, GESTIONNAIRE_STOCK, VENDEUR, COMPTABLE, LIVREUR, SERVICE_CLIENT)."

    def handle(self, *args, **options):
        for nom, regles in ROLES.items():
            if regles is None:
                self.stdout.write(f'{nom} → géré via is_superuser, pas de groupe créé.')
                continue
            groupe, cree = Group.objects.get_or_create(name=nom)
            permissions = []
            for app_label, actions in regles.items():
                qs = Permission.objects.filter(content_type__app_label=app_label)
                if actions != '__all__':
                    qs = qs.filter(codename__regex=r'^(' + '|'.join(actions) + ')_')
                permissions.extend(qs)
            groupe.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f'{"Créé" if cree else "Mis à jour"} : {nom} ({len(permissions)} permissions)'))
