from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Adresse

Utilisateur = get_user_model()


class UtilisateurSerializer(serializers.ModelSerializer):
    prenom = serializers.CharField(source='first_name')
    nom = serializers.CharField(source='last_name', required=False, allow_blank=True)

    class Meta:
        model = Utilisateur
        fields = ['id', 'prenom', 'nom', 'email', 'telephone']


class InscriptionSerializer(serializers.ModelSerializer):
    prenom = serializers.CharField(source='first_name')
    nom = serializers.CharField(source='last_name', required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Utilisateur
        fields = ['prenom', 'nom', 'email', 'telephone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data['email']
        utilisateur = Utilisateur(username=email, **validated_data)
        utilisateur.set_password(password)
        utilisateur.save()
        return utilisateur


class AdresseSerializer(serializers.ModelSerializer):
    parDefaut = serializers.BooleanField(source='par_defaut', required=False, default=False)

    class Meta:
        model = Adresse
        fields = ['id', 'label', 'ville', 'commune', 'quartier', 'details', 'parDefaut']

    def create(self, validated_data):
        validated_data['utilisateur'] = self.context['request'].user
        return super().create(validated_data)
