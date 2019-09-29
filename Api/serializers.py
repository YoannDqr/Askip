from rest_framework import serializers
from Comif.models import *
from Codypen.models import *


class ProduitSerializer(serializers.ModelSerializer):
	class Meta:
		model = Produit
		fields = ('pk', 'nom', 'prix', 'stock', 'prix_achat')


class CategorieSerializer(serializers.ModelSerializer):
	produits = ProduitSerializer(many=True)

	class Meta:
		model = Categorie
		fields = ('pk', 'nom', 'produits')


class TypeSerializer(serializers.ModelSerializer):
	categories = CategorieSerializer(many=True)

	class Meta:
		model = Type
		fields = ('pk', 'nom', 'categories')


class UtilisateurSerializer(serializers.ModelSerializer):
	class Meta:
		model = Utilisateur
		fields = ('pk', 'first_name', 'last_name', 'photo')


class ClientSerializer(serializers.ModelSerializer):
	# Redefine the .create method to be able to change this field through
	# the ClientSerializer object via POST request.
	utilisateur = UtilisateurSerializer(read_only=True)

	class Meta:
		model = Client
		fields = ('pk', 'first_name', 'last_name', 'solde', 'cotisant', 'utilisateur')


class AssociationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Association
		fields = ('pk', 'nom')


class AchatSerializer(serializers.ModelSerializer):
	class Meta:
		model = Achat
		fields = ('pk', 'description', 'date', 'prix')


class DossierSerializer(serializers.ModelSerializer):
	utilisateur = UtilisateurSerializer(read_only=True)

	class Meta:
		model = Dossier
		fields = ('utilisateur', 'pk', 'path', 'date_creation', 'last_modification', )


class FichierSerializer(serializers.ModelSerializer):
	class PermissionSerializerFichier(serializers.ModelSerializer):
		class Meta:
			model = Permission
			fields = ('user', 'read', 'write')

	utilisateur = UtilisateurSerializer()
	permission_set = PermissionSerializerFichier(many=True, read_only=True)

	class Meta:
		model = Fichier
		fields = ('utilisateur', 'pk', 'path', 'file', 'date_creation', 'last_modification', 'permission_set')


class PermissionSerializer(serializers.ModelSerializer):
	fichier = FichierSerializer(read_only=True)
	user = UtilisateurSerializer(read_only=True)
	class Meta:
		model = Permission
		fields = ('user', 'fichier','read', 'write')


class MessageSerializer(serializers.ModelSerializer):
	receiver = UtilisateurSerializer(many=True, read_only=True)
	sender = UtilisateurSerializer(read_only=True)
	class Meta:
		model = Message
		fields = ('pk', 'receiver', 'sender', 'message', 'date', 'file')








