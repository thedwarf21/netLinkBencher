#!/usr/bin/python3.5
# -*-coding:utf-8 -*

class Element:

	"""Classe définissant un noeud (ou le tronc) d'une arborescence.

	Cette classe a pour voccation de permettre la manipulation de la
	strucuture des arborescences générées par GenericParser.

	Attributs:
	  - tag : le tag de l'élément.
	  - children : la liste des éléments fils.
	  - properties : dictionnaire des propriétés de l'élément.
	  - parent : père de l'élément.
	  - valeur : texte entre la balise ouvrante et la balise fermante.
	  - niveau : niveau d'indentation.

	"""

	def __init__(self, tag, pere=None, valeur="", **properties):
		"""Constructeur de la classe attendant le tag de la balise.

		En l'absence du paramètre 'pere' il s'agit d'un tronc vierge.
		sinon on ajoute l'élément aux fils de celui passé en paramètre.
		Il peut recevoir une valeur s'il n'a pas de pere.
		Il peut également recevoir un dictionnaire de propriétés.

		"""
		self.tag = tag
		self.children = list()
		self.properties = properties
		if pere is not None:
			self.parent = pere
			self.valeur = valeur
			self.niveau = pere.niveau + 1
			pere.appendChild(self)
		else:
			self.parent = None
			self.valeur = ""
			self.niveau = 0
			self.properties = dict()

	def __str__(self):
		"""Méthode d'affichage de la classe."""
		str_indent = self.indent("    ")
		retour = str_indent
		str_props = ""
		for name, value in self.properties.items():
			str_props += " " + name + "=" + value
		# S'il y a une valeur on l'affiche avec la balise fermante sur la même ligne sauf si on a des \n dans la valeur.
		if self.valeur != "":
			if self.valeur.find("\n") == -1:
				retour += "<" + self.tag + str_props + ">" + self.valeur + "</" + self.tag + ">\n"
			else:
				retour += "<" + self.tag + str_props + ">\n"
				for ligne in self.valeur.split("\n"):
					retour += str_indent + ligne + "\n"
				retour += str_indent + "</" + self.tag + ">\n"
		else:
			# Si n'y a pas de fils c'est que c'est une auto-fermante.
			if self.children:
				retour += "<" + self.tag + str_props + ">\n"
				# Affichage des enfants
				for fils in self.children:
					retour += str(fils)
				retour += str_indent + "</" + self.tag + str_props + ">\n"
			else:
				retour += "<" + self.tag + str_props + ">\n"
		return retour

	def appendChild(self, fils):
		"""Méthode permettant d'ajouter un fils à l'élément."""
		self.children.append(fils)

	def indent(self, indentation):
		"""Méthode de génération de l'indentation."""
		retour = ""
		i = 0
		while i < self.niveau:
			retour += indentation
			i += 1
		return retour

	def getChild(self, tag):
		"""Méthode de récupération d'un enfant de l'élément en fonction de son tag."""
		for child in self.children:
			if child.tag == tag:
				return child
		return None