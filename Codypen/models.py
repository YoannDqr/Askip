# -*- coding: utf8 -*-
from __future__ import unicode_literals

from django.db import models

from Cotisation.models import Utilisateur

import os

# Create your models here.


class DossierException(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return "DossierException raised" + format(self.value)


class Dossier(models.Model):
	utilisateur = models.ForeignKey(Utilisateur, related_name="dossier")
	path = models.TextField()
	date_creation = models.DateField(auto_now=True)
	last_modification = models.DateField(auto_now=True)

	def save(self, *args, **kwargs):
		list_dossier = Dossier.objects.filter(path=self.path,utilisateur=self.utilisateur)
		clean = (
			#(self.permission in ('read', 'write', '')) and
			(len(list_dossier) == 0 or len(list_dossier.filter(pk=self.pk)) > 0)
		)
		if clean:
			super(Dossier, self).save()

		else:
			raise ValueError("Parameters don't match")

	def get_parent(self):
		parent_path = self.path.split('/')
		parent_path = '/'.join(parent_path[:len(parent_path) - 1])
		if parent_path == '':
			parent_path = '/'
		parent = Dossier.objects.filter(utilisateur=self.utilisateur, path=parent_path)
		if len(parent) >= 0:
			return parent[0]
		else:
			self.erase()

	def get_content(self):
		content = Dossier.objects.none()
		for dossier in Dossier.objects.filter(utilisateur=self.utilisateur):
			if dossier != self and self == dossier.get_parent():
				content |= Dossier.objects.filter(pk=dossier.pk)
		return content

	def erase(self):
		for dossier in Dossier.objects.filter(utilisateur=self.utilisateur):
			if self.path in dossier.path:
				dossier.delete()

	def set_name(self, name):
		index = len(self.path.split('/'))
		for dossier in Dossier.objects.filter(utilisateur=self.utilisateur):
			if (self.path in dossier.path) and (self != dossier):
				mem = dossier.path.split('/')
				mem[index - 1] = name
				mem = '/'.join(mem)
				dossier.path = mem
				dossier.save()
		mem = self.path.split('/')
		mem[index-1] = name
		self.path = '/'.join(mem)
		self.save()

	def __str__(self):
		return self.path.encode('utf8')

	def delete(self, using=None, keep_parents=False):
		try:
			fichier = Fichier.objects.get(path=self.path, utilisateur=self.utilisateur)
			os.remove(fichier.file.path)
		except:
			pass
		super(Dossier, self).delete(using=using, keep_parents=False)


class Fichier(Dossier):
	file = models.FileField(upload_to='file_upload')


class Permission(models.Model):
	"""
	Les permissions s'appliquent uniquement pour les dossiers n'appartenant pas à l'utilisateur souhaitant l'utiliser.
	"""
	dossier = models.ForeignKey(Dossier)
	user = models.ForeignKey(Utilisateur)
	read = models.BooleanField(default=False)
	write = models.BooleanField(default=False)

	def __str__(self):
		return format(self.user) + ' ' + format(self.dossier)

	def get_content(self):
		content = self.dossier.get_content()
		content_perm = Permission.objects.none()
		for elt in content:
			dossier = elt.permission_set.get(user=self.user)
			content_perm |= Dossier.objects.filter(pk=elt.pk)
		return content_perm

	@staticmethod
	def create_recursive_permissions(dossier, user):
		try:
			Fichier.objects.get(pk=dossier.pk)
		except Fichier.DoesNotExist:
			for dir in dossier.get_content():
				Permission.create_recursive_permissions(dir, user)
		try:
			Permission.objects.get(dossier=dossier, user=user)
		except Permission.DoesNotExist:
			permission = Permission(dossier=dossier, user=user)
			permission.save()

	@staticmethod
	def delete_recursive_permissions(dossier, user):
		try:
			Fichier.objects.get(pk=dossier.pk)
		except:
			for dir in dossier.get_content():
				Permission.delete_recursive_permissions(dir, user)
		try:
			Permission.objects.get(dossier=dossier, user=user).delete()

		except Permission.DoesNotExist:
			pass


class Message(models.Model):
	sender = models.ForeignKey(Utilisateur, related_name='sended_message')
	receiver = models.ManyToManyField(Utilisateur, related_name='received_message')
	message = models.TextField(blank=True)
	file = models.FileField(upload_to="chat_upload_file", null=True)
	date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return format(self.sender).encode('utf8') + " : " + self.message.encode('utf8')

