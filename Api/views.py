# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework import permissions, generics
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication

from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer
from rest_framework.permissions import IsAuthenticated

from Cotisation.models import *
from Comif.models import *
from .serializers import *

from Codypen.models import *


class JSONWebTokenAuthenticationQS(BaseJSONWebTokenAuthentication):
	def get_jwt_value(self, request):
		if 'jwt' in request.data:
			return request.data['jwt']
		elif 'jwt' in request.GET:
			return request.GET['jwt']
		elif 'jwt' in request.POST:
			return request.POST['jwt']
		else:
			return ""


def index(request):
	return render(request, 'api/index.html', {})


class Utilisateurs(generics.ListCreateAPIView):
	# authentication_classes = (JSONWebTokenAuthenticationQS,)
	queryset = Utilisateur.objects.all()
	serializer_class = UtilisateurSerializer


class Users(generics.ListCreateAPIView):
	"""
		Send QuerySets related to users
	"""
	# permission_classes = (IsAuthenticated,)
	queryset = Client.objects.all()
	serializer_class = ClientSerializer


class Produits(APIView):
	""" List all products related to the <Type> given as a GET parameter """

	def get(self, request):
		# POST = JSONParser().parse(request)
		if 'type' in request.GET:
			try:
				type = Type.objects.get(pk=request.GET['type'])
			except Type.DoesNotExist:
				return HttpResponse(status=404)

			# We list only vategories related to the <Type> targeted.
			categories = type.categories.all()
			response = CategorieSerializer(categories, many=True).data
			return Response(response, status=200, content_type="application/json")
		else:
			return Response(status=204)


class Associations(APIView):
	"""List associations related to the user whose id is given in the GET Django object"""

	def get(self, request):
		if 'id' in request.GET:
			id = request.GET['id']
			user = Utilisateur.objects.none()
			try:
				user = Utilisateur.objects.get(pk=id)
			except:
				user = Utilisateur.objects.none

			cotisations = user.cotisation_set.all()
			associations = Association.objects.none()

			for cotisation in cotisations:
				associations = associations | Association.objects.filter(pk=cotisation.association.pk)

			if len(associations) > 0:
				response = AssociationSerializer(associations, many=True).data
				return Response(response, status="200")
			else:
				return Response(status=204)

		else:
			return Response(status=204)


class Achats(APIView):
	authentication_classes = (JSONWebTokenAuthenticationQS,)

	def post(self, request):

		POST = request.data
		if 'user_id' in POST and 'association' in POST:
			user = get_object_or_404(Client, pk=POST['user_id'])
			produits = []
			produits_error = []

			for key, value in POST.items():
				if 'produit_' in key:
					id = value

					qte = POST['qte_' + format(id)]
					try:
						produit = Produit.objects.get(pk=id)
						produits.append((produit, qte))
					except:
						produits_error.append(id)

			if len(produits) > 0:
				association = get_object_or_404(Association, pk=POST['association'])
				commande = Achat(utilisateur=user, description="", association=association)
				commande.save()
				for produit, qte in produits:
					if user.solde - produit.prix * qte >= 0:
						commande.produits.add(produit)
						commande.description += produit.nom + ' x ' + format(qte)
						commande.prix = produit.prix * qte
						user.solde -= produit.prix * qte
					else:
						produits_error.append(produit.pk)
				user.save()
				commande.save()
				return Response(produits_error, status=200)
			else:
				return Response(status=204)


class Reload(APIView):
	def put(self, request):
		PUT = request.data
		if 'user_id' in PUT and 'association' in PUT and 'value' in PUT and PUT['value'] > 0:
			user = Client.objects.none()
			try:
				association = Association.objects.get(pk=PUT['association'])
				user = Client.objects.get(pk=PUT['user_id'])
				user.solde += PUT['value']
				rechargement = Achat(
					utilisateur=user,
					description="Rechargement de " + format(PUT['value']),
					association=association,
					prix=PUT['value']
				)
				rechargement.save()
				user.save()
				response = ClientSerializer(user).data
				return Response(response, status=200)
			except:
				return Response(status=204)
		return Response(status=204)


class History(APIView):
	def get(self, request):
		GET = request.GET
		if 'user_id' in GET and 'association' in GET:
			try:
				user = Client.objects.get(pk=GET['user_id'])
				association = Association.objects.get(pk=GET['association'])
				history = Achat.objects.filter(association=association, utilisateur=user).order_by('-date')
				response = AchatSerializer(history, many=True).data
				return Response(response, status=200)
			except:
				return Response(response, status=204)
		return Response(response, status=204)


class Types(APIView):
	def get(self, request):
		types = Type.objects.all()
		response = TypeSerializer(types, many=True).data
		return Response(response, status=200)

	def post(self, request):
		if 'new_type' in request.data and 'association' in request.data:
			association = Association.objects.none()
			try:
				association = Association.objects.get(pk=request.data['association'])
				type = Type(nom=request.data['new_type'], association=association)
				type.save()
				response = TypeSerializer(type).data
				return Response(response, status=200)
			except:
				return Response(status=204)
		return Response(status=204)

	def delete(self, request):
		if 'id' in request.GET:
			try:
				type = Type.objects.get(pk=request.GET['id'])
				type.delete()
				return Response(status=200)
			except:
				return Response(status=204)
		return Response(status=204)


class Categories(APIView):
	def get(self, request):
		categories = Categorie.objects.all()
		response = CategorieSerializer(categories, many=True)
		return Response(response, status=200)

	def post(self, request):
		if 'new_categorie' in request.data and 'association' in request.data:
			association = Association.objects.none()
			try:
				association = Association.objects.get(pk=request.data['association'])
				categorie = Categorie(nom=request.data['new_categorie'], association=association)
				categorie.save()
				response = CategorieSerializer(categorie).data
				return Response(response, status=200)
			except:
				return Response(status=204)
		return Response(status=204)

	def delete(self, request):
		if 'id' in request.GET:
			try:
				categorie = Categorie.objects.get(pk=request.GET['id'])
				categorie.delete()
				return Response(status=200)
			except:
				return Response(status=204)

		return Response(status=204)


class CategoriesMiss(APIView):
	def get(self, request):
		categories = Categorie.objects.all()
		categorieMiss = Categorie.objects.none()

		for categorie in categories:
			if len(categorie.type_set.all()) == 0:
				categorieMiss |= Categorie.objects.filter(pk=categorie.pk)
		if len(categorieMiss) == 0:
			return Response(status=204)
		response = CategorieSerializer(categorieMiss, many=True).data
		return Response(response, status=200)


class ManageDirectories(APIView):
	authentication_classes = (JSONWebTokenAuthenticationQS,)

	def get(self, request):
		"""
		parametre isFile : true => renvoie si le path est relatif à un fichier ou un dossier
		"""
		user = get_object_or_404(Utilisateur, pk=request.GET['user_id'])
		try:
			if 'isFile' in request.GET:
				root = Fichier.objects.get(path=request.GET['root'], utilisateur=user)
				response = FichierSerializer(root).data
			else:
				if request.GET['root'] == '/':
					root = Dossier.objects.get(path=request.GET['root'], utilisateur=user)
				else:
					root = Dossier.objects.get(pk=request.GET['root'], utilisateur=user)

				memory = root.get_content()
				root = memory
				root_file = Fichier.objects.none()
				for elt in memory:
					try:
						root_file |= Fichier.objects.filter(pk=Fichier.objects.get(pk=elt.pk).pk)
						root = root.exclude(pk=elt.pk)
					except:
						pass

				response = DossierSerializer(root, many=True).data + FichierSerializer(root_file, many=True).data

			return Response(response, status=200)
		except:
			return Response(status=204)

	def post(self, request):
		"""
		Create a directory
		"""
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		try:
			dossier = Dossier(path=request.data['path'], utilisateur=user)
			dossier.save()
		except:
			return Response(status=204)
		response = DossierSerializer(dossier).data

		return Response(response, status=200)

	def delete(self, request):
		"""
		Delete recursively file and directory
		"""
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		try:
			file = Dossier.objects.get(path=request.data['path'], utilisateur=user)
			file.erase()
		except:
			return Response(status=400)
		response = DossierSerializer(file).data
		return Response(response, status=200)

	def patch(self, request):
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		try:
			dossier = Dossier.objects.get(path=request.data['old'], utilisateur=user)
			dossier.set_name(request.data['new'].split('/')[-1])
		except:
			return Response(status=400)
		response = DossierSerializer(dossier).data
		return Response(response, status=200)


class File(APIView):
	def get(self, request):
		"""
		Return the file object related to the dossier object given through it pk in the GET dict.
		Return 400 error if any problems occured : permission not valid, dossier isn't a file...
		Return the file object serialized if it eist and the user is able to see it.
		"""
		if 'user_id' in request.GET and 'pk' in request.GET:
			user = get_object_or_404(Utilisateur, pk=request.GET['user_id'])
			dossier = get_object_or_404(Dossier, pk=request.GET['pk'])
			try:
				permission = Permission.objects.get(user=user, dossier=dossier)
			except Permission.DoesNotExist:
				return Response(status=400)
			try:
				fichier = Fichier.objects.get(pk=dossier.pk)
			except Fichier.DoesNotExist:
				return Response(status=400)
			response = FichierSerializer(fichier).data
			return Response(response, status=200)

		elif 'user_id' in request.GET and 'load_torrent' in request.GET:

			directories = subprocess.check_output('ls /var/lib/transmission-daemon/downloads').split('\n')


		return Response(status=400)

	def post(self, request):
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		try:
			file = Fichier(path=request.data['path'], utilisateur=user, file=request.FILES['file'])
			file.save()
		except:
			return Response(status=204)
		response = FichierSerializer(file).data
		return Response(response, status=200)

def extract_file_from_directory(self, path):
	import subprocess
	try:
		directories = subprocess.check_output('ls ' + path).split('\n')
	except:
		return [path]

	path_list = []
	for current_path in directories:
		if path == '/':
			cte_path = ''
		else:
			cte_path = path
		path_list += self.extract_file_from_directory(cte_path + '/' + current_path)
	return path_list



class Permissions(APIView):
	def get(self, request):
		user = get_object_or_404(Utilisateur, pk=request.GET['user_id'])

		if 'pk' in request.GET:
			# Only permission of a given file
			dossier = get_object_or_404(Dossier, pk=request.GET['pk'])
			if user == dossier.utilisateur:
				response = PermissionSerializer(dossier.permission_set.all(), many=True).data
				return Response(response, status=200)
			else:
				return Response(status=204)
		elif 'path' in request.GET:
			permissions_file = Fichier.objects.none()
			if request.GET['path'] == 'shared':
				permissions = Dossier.objects.none()
				for perm in Permission.objects.filter(user=user):
					parent_permission = perm.dossier.get_parent().permission_set.all()
					try:
						parent_permission = parent_permission.get(user=user)
					except Permission.DoesNotExist:
						if len(Fichier.objects.filter(pk=perm.dossier.pk)) > 0:
							permissions_file |= Fichier.objects.filter(pk=perm.dossier.pk)
						else:
							permissions |= Dossier.objects.filter(pk=perm.dossier.pk)
			else:
				try:
					dossier = Dossier.objects.get(pk=request.GET['path'])
					permissions = Permission.objects.get(dossier=dossier, user=user)
				except:
					return Response(status=400)

				permissions = permissions.get_content()
				for perm in permissions:
					if len(Fichier.objects.filter(pk=perm.pk)) > 0:
						permissions_file |= Fichier.objects.filter(pk=perm.pk)

				for elt in permissions_file:
					permissions = permissions.exclude(pk=elt.pk)

			response = DossierSerializer(permissions, many=True).data + FichierSerializer(permissions_file,
			                                                                              many=True).data
			return Response(response, status=200)
		else:
			return Response(status=404)

	def post(self, request):
		if not ('user_id' in request.data and 'useradded_id' in request.data and 'pk' in request.data):
			return Response(status=400)

		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		user_add = get_object_or_404(Utilisateur, pk=request.data['useradded_id'])
		dossier = get_object_or_404(Dossier, pk=request.data['pk'], utilisateur=user)
		Permission.create_recursive_permissions(dossier, user_add)

		permission = Permission.objects.get(dossier=dossier, user=user_add)
		permission.save()
		response = PermissionSerializer(permission).data

		return Response(response, status=200)

	def delete(self, request):
		if not ('user_id' in request.data and 'useradded_id' in request.data and 'pk' in request.data):
			return Response(status=400)
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		user_add = get_object_or_404(Utilisateur, pk=request.data['useradded_id'])
		dossier = get_object_or_404(Dossier, pk=request.data['pk'], utilisateur=user)
		Permission.delete_recursive_permissions(dossier, user_add)
		return Response(status=204)


def qegale(query1, query2):
	for elt in query1:
		if not (elt in query2):
			return False
	return len(query1) == len(query2)


class Messages(APIView):
	def get(self, request):
		user = get_object_or_404(Utilisateur, pk=request.GET['user_id'])
		if 'all_for_user' in request.GET:
			return self.find_conversations(user)
		elif 'conv_id' in request.GET:
			return self.find_one_conversation(request, user)
		elif 'last' in request.GET:
			return self.get_last_message(request, user)
		elif 'receiver_id' in request.GET:
			return self.know_user(request, user)
		else:
			return Response(status=400)

	def post(self, request):
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])

		if 'message' in request.data and 'receiver_id' in request.data:
			receiver = get_object_or_404(Utilisateur, pk=request.data['receiver_id'])
			group = Utilisateur.objects.filter(pk=user.pk)
			group |= Utilisateur.objects.filter(pk=receiver.pk)
			messages = Messages.extract_conversation(group, user.received_message.all())
			if len(messages) > 0:
				return Response(status=400)  # Conversation déjà créee ! Pas d'envoie du message
			response = Messages.send_message(user, request.data['message'], group)
			return Response(response, status=200)

		if 'message' in request.data and 'active_conv' in request.data:
			msg = get_object_or_404(Message, pk=request.data['active_conv'])
			if not (user in msg.receiver.all()):
				return Response(status=400)
			response = Messages.send_message(user, request.data['message'], msg.receiver.all())
			return Response(response, status=200)

		if 'user_list' in request.data and 'conv_id' in request.data:
			msg = get_object_or_404(Message, pk=request.data['conv_id'])
			new_message = Message(sender=user, message="Une conversation de groupe a été créée")
			new_message.save()
			for receiver in msg.receiver.all():
				new_message.receiver.add(receiver)
			new_message.save()

			for key, value in request.data.items():
				if 'user_id_' in key:
					user = get_object_or_404(Utilisateur, pk=value)
					new_message.receiver.add(user)
			new_message.save()

			old_conversation = Messages.extract_conversation(new_message.receiver.all(), user.received_message.all())
			if len(old_conversation) > 1:
				new_message.delete()
				response = MessageSerializer(old_conversation[1]).data
				return Response(response, status=204)
			response = MessageSerializer(new_message).data
			return Response(response, status=200)

		if 'upload_file' in request.data and 'conv_id' in request.data and 'file' in request.FILES:
			conv = get_object_or_404(user.received_message, pk=request.data['conv_id'])
			try:
				upload_file = Message(sender=user, file=request.FILES['file'])
				upload_file.save()
			except:
				return Response('File not uploaded', status=400)
			for user in conv.receiver.all():
				upload_file.receiver.add(user)
			upload_file.save()
			response = MessageSerializer(upload_file).data
			return Response(response, status=200)

		return Response(status=400)

	def delete(self, request):
		user = get_object_or_404(Utilisateur, pk=request.data['user_id'])
		if 'conv_id' in request.data:
			message = get_object_or_404(Message, pk=request.data['conv_id'])
			conversation = self.extract_conversation(message.receiver.all(), user.received_message.all())
			conversation.delete()
			return Response(status=204)
		return Response(status=400)

	@staticmethod
	def send_message(user, message, receivers):
		message = message.split('\n')
		message = '<br>'.join(message)
		new_msg = Message(sender=user, message=message)
		new_msg.save()
		for elt in receivers:
			new_msg.receiver.add(elt)
		new_msg.save()
		response = MessageSerializer(new_msg).data
		return response

	@staticmethod
	def extract_conversation(group, message_base):
		messages = Message.objects.none()
		for message in message_base:
			if qegale(message.receiver.all(), group):
				messages |= message_base.filter(pk=message.pk)
		return messages.order_by('date')

	def get_last_message(self, request, user):
		message = get_object_or_404(Message, pk=request.GET['last'])
		conv = self.extract_conversation(message.receiver.all(), user.received_message.all())
		conv = conv.exclude(date__lte=message.date).order_by('date')
		response = MessageSerializer(conv, many=True).data
		return Response(response, status=200)

	def find_conversations(self, user):
		conversations = Message.objects.none()
		message_tested = Message.objects.none()

		for message in user.received_message.all():
			if message in message_tested:
				continue

			last_message = Messages.extract_conversation(message.receiver.all(), user.received_message.all())
			message_tested |= last_message
			last_message = last_message.order_by('-date')
			if not (last_message is None) and len(last_message) > 0 and not (last_message[0] in conversations):
				conversations |= Message.objects.filter(pk=last_message[0].pk)

		response = [UtilisateurSerializer(user).data] + MessageSerializer(conversations.order_by('-date'),
		                                                                  many=True).data
		return Response(response, status=200)

	def find_one_conversation(self, request, user):
		message = user.received_message.filter(pk=request.GET['conv_id'])

		if len(message) != 1:
			return Response(400)

		group = message[0].receiver.all()
		messages = Messages.extract_conversation(group, user.received_message.all())
		response = MessageSerializer(messages, many=True).data

		return Response(response, status=200)

	def know_user(self, request, user):
		receiver_id = request.GET['receiver_id']
		receiver = get_object_or_404(Utilisateur, pk=receiver_id)
		group = Utilisateur.objects.filter(pk=user.pk) | Utilisateur.objects.filter(pk=receiver.pk)
		messages = Messages.extract_conversation(group, user.received_message.all())
		if len(messages) > 0:
			response = MessageSerializer(messages, many=True).data
			return Response(response, status=200)
		return Response(status=204)


"""
class Types(generics.ListCreateAPIView):
	# authentication_classes = (JSONWebTokenAuthenticationQS,)
	queryset = Type.objects.all()
	serializer_class = TypeSerializer
"""
