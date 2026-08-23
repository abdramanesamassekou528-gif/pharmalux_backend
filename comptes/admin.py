from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Adresse, Utilisateur


class AdresseInline(admin.TabularInline):
    model = Adresse
    extra = 0


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ['email', 'first_name', 'last_name', 'telephone', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'groups']
    search_fields = ['email', 'first_name', 'last_name', 'telephone']
    ordering = ['email']
    inlines = [AdresseInline]
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'telephone')}),
        ('Rôles & permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}),
    )


@admin.register(Adresse)
class AdresseAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'label', 'commune', 'ville', 'par_defaut']
    search_fields = ['utilisateur__email', 'commune', 'quartier']
