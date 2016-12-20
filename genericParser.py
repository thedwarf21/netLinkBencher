#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import os
dir_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_path)

from element import Element

class GenericParser:

	"""Classe de parsing générique.

	Cette classe a pour voccation d'être héritée par divers parser selon le besoin.

	Attributs:
	  - stream : flux de données à parser.
	  - data : variable temporaire pour les données entre balises.

	"""

	def __init__(self):
		"""Constructeur de la classe attendant un nom de fichier en paramètre.

		Il ouvre le fichier et analyse le flux.
		Il appelle à la volée des méthodes spécifiques au type de balise rencontré.
		Ces méthodes sont à surcharger dans les classes filles.

		"""
		self.stream = ""
		self.data = ""
		
	def parse(self):
		"""Méthode effectuant le parsing du flux."""
		self.start_document()
		idx_deb, idx_fin = 0, 0
		# On parcourt le flux.
		while idx_deb != -1:
			# Détection d'une balise.
			idx_deb = self.stream.find("<", idx_fin)
			# Si on ne trouve plus de balise c'est qu'on est en fin de document.
			if idx_deb == -1:
				break
			# On récupère les éventuelles données entre la balise précédente et celle-ci.
			donnees = self.stream[idx_fin:idx_deb].strip()
			if donnees != "":
				self.data = donnees
			idx_fin = self.stream.find(">", idx_deb) + 1
			balise = self.stream[idx_deb:idx_fin].strip()

			# On appelle la méthode idoine suivant le cas.
			if balise[:3] == "<!#" or balise[:2] == "<?" or balise[:5] == "<!--[" or \
				balise == "<![endif]-->" or balise[:9] == "<!DOCTYPE":
				if balise[2:5] != "xml":
					self.open_instruction(balise)
			elif balise[:4] == "<!--":
				self.open_commentaire(balise)
			elif balise[1] == "/":
				self.end_element(balise)
			elif balise[-2] == "/":
				self.start_element(balise)
				self.end_element(balise)
			else:
				self.start_element(balise)
		self.end_document()

	def start_document(self):
		"""Méthode invoquée avant l'analyse du document."""

	def end_document(self):
		"""Méthode invoquée après l'analyse du document."""

	def open_commentaire(self, balise):
		"""Méthode invoquée lorsque le parser détecte un commentaire."""

	def open_instruction(self, balise):
		"""Méthode invoquée lorsque le parser détecte une PI ou autre instruction."""

	def start_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise ouvrante."""

	def end_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise fermante."""


#####################
# Parser de fichier #
#####################
class FileParser(GenericParser):

	"""Classe de parsing de fichier.

	Cette classe a voccation d'être héritée.
	Elle intègre la lecture d'un fichier dans le constructeur afin d'alimenter le flux.

	Attributs:
	  - niv_indent : niveau d'indentation.

	"""

	def __init__(self, nom_fichier):
		"""Constructeur de la classe recevant le nom du fichier à mettre en forme."""
		self.niv_indent = 0
		GenericParser.__init__(self)
		# Alimentation du flux.
		with open(nom_fichier) as file:
			self.stream = file.read()

	def format_as(self, nom_fichier):
		"""Méthode de sauvegarde du fichier reformatté dans un autre fichier."""
		with open(nom_fichier, "w") as file:
			file.write(str(self))

#########################
# Parser de fichier XML #
#########################
class XmlFileParser(FileParser):
	
	"""Classe de parsing de fichier XML.

	Cette classe ouvre un fichier xml et en permet la manipulation 
	simplement en le mettant sous la forme d'un arbre.

	Attributs:
	  - top_comm : commentaire de haut de document.
	  - top_instruc : liste des instruction en haut du document.
	  - document : pointeur vers la balise maîtresse.
	  - curElement : pointeur vers le noeud de travail courant.

	"""

	def __init__(self, nom_fichier):
		"""Constructeur de la classe recevant le nom du fichier à mettre en forme."""
		FileParser.__init__(self, nom_fichier)
		self.top_comm = None
		self.document = None
		self.curElement = None
		self.top_instruc = list()
		FileParser.parse(self)

	def __str__(self):
		"""Méthode d'affichage de la classe."""
		retour = "<?xml version='1.0'?>\n"
		if self.top_instruc:
			for instr in self.top_instruc:
				retour += str(instr)
		if self.top_comm is not None:
			retour += str(self.top_comm)
		retour += str(self.document)
		return retour

	def open_commentaire(self, balise):
		"""Méthode invoquée lorsque le parser détecte un commentaire."""
		# Si on est sur la première balise on initialise document.
		content = balise[1:-1].strip()
		if self.document is None:
			self.top_comm = Element(content)
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			Element(content, pere=self.curElement)

	def open_instruction(self, balise):
		"""Méthode invoquée lorsque le parser détecte une PI ou autre instruction."""
		# Si on est sur la première balise on initialise document.
		content = balise[1:-1].strip()
		if self.document is None:
			self.top_instruc.append(Element(content))
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			Element(content, pere=self.curElement)

	def start_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise ouvrante."""
		tag = ""
		properties = dict()
		content = balise[1:-1].strip()
		idx = content.find(" ")
		# Tag seul ou balise porteuse de propriétés ?
		if idx == -1:
			tag = content
		else:
			tag = content[:idx]
			content = content [idx + 1:].split("=")
			prop_name = content[0].strip()
			i = 1
			while prop_name != "" and i < len(content):
				val = content[i].strip()
				# Si la valeur de la propriété est une chaîne de caractères.
				if val[0] == '"' or val[0] == "'":
					idx = val.find(val[0],1)
					properties[prop_name] = val[1:idx]
				# Sinon c'est une valeure brute.
				else:
					idx = val.find(" ")
					properties[prop_name] = val[:idx]
				# La fin est le nom de la propriété suivante.
				prop_name = val[idx + 1:].strip()
				i += 1
		# Si on est sur la première balise on initialise document.
		if self.document is None:
			self.document = Element(tag, **properties)
			self.curElement = self.document
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			self.curElement = Element(tag, pere=self.curElement, **properties)

	def end_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise fermante."""
		# On met à jour la balise courante avec les données s'il y en a.
		if self.data != "":
			self.curElement.valeur = self.data
			self.data = ""
		# On repositionne le pointeur courant sur le père.
		self.curElement = self.curElement.parent

	def save_as_html(self, nom_fichier):
		"""Méthode permettant de le rendre lisible dans un navigateur au format html en remplaçant :
		  - les ' ' par &nbsp;
		  - les '<' par &lt;
		  - les '>' par &gt;
		  - les '\n' par des <br/>

		  """
		with open(nom_fichier, "w") as file:
			file.write(str(self).replace(" ", "&nbsp;").replace("<", "&lt;").replace(">","&gt;").replace("\n", "<br/>"))


##########################
# Parser de fichier HTML #
##########################
class HtmlFileParser(FileParser):
	
	"""Classe de parsing de fichier HTML.

	Cette classe ouvre un fichier html et en permet la manipulation 
	simplement en le mettant sous la forme d'un arbre.

	Attributs:
	  - top_comm : commentaire de haut de document.
	  - top_instruc : liste des instruction en haut du document.
	  - document : pointeur vers la balise maîtresse.
	  - curElement : pointeur vers le noeud de travail courant.

	"""

	def __init__(self, nom_fichier):
		"""Constructeur de la classe recevant le nom du fichier à mettre en forme."""
		FileParser.__init__(self, nom_fichier)
		self.top_comm = None
		self.document = None
		self.curElement = None
		self.top_instruc = list()
		FileParser.parse(self)

	def __str__(self):
		"""Méthode d'affichage de la classe."""
		retour = ""
		if self.top_instruc:
			for instr in self.top_instruc:
				retour += str(instr)
		if self.top_comm is not None:
			retour += str(self.top_comm)
		retour += str(self.document)
		return retour

	def open_commentaire(self, balise):
		"""Méthode invoquée lorsque le parser détecte un commentaire."""
		# Si on est sur la première balise on initialise document.
		content = balise[1:-1].strip()
		if self.document is None:
			self.top_comm = Element(content)
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			Element(content, pere=self.curElement)

	def open_instruction(self, balise):
		"""Méthode invoquée lorsque le parser détecte une PI ou autre instruction."""
		# Si on est sur la première balise on initialise document.
		content = balise[1:-1].strip()
		if self.document is None:
			self.top_instruc.append(Element(content))
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			Element(content, pere=self.curElement)

	def start_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise ouvrante."""
		tag = ""
		properties = dict()
		content = balise[1:-1].strip().replace("\n","")
		idx = content.find(" ")
		# Tag seul ou balise porteuse de propriétés ?
		if idx == -1:
			tag = content
		else:
			tag = content[:idx]
			content = content[idx + 1:].split("=")
			prop_name = content[0].strip()
			i = 1
			while prop_name != "" and i < len(content):
				val = content[i].strip()
				# Si la valeur de la propriété est une chaîne de caractères.
				if val[0] == '"' or val[0] == "'":
					idx = val.find(val[0],1)
					properties[prop_name] = val[:idx]
				# Sinon c'est une valeure brute.
				else:
					idx = val.find(" ",0)
					properties[prop_name] = val[:idx]
				# La fin est le nom de la propriété suivante.
				prop_name = val[idx + 1:].strip()
				i += 1
		# Si on est sur la première balise on initialise document.
		if self.document is None:
			self.document = Element(tag, **properties)
			self.curElement = self.document
		# Sinon on gère l'élément comme un fils de l'élément courant.
		else:
			self.curElement = Element(tag, pere=self.curElement, **properties)
		# Si on est dans le cas d'une balise qui devrait être une autofermante mais qui ne l'est pas (html sale).
		if content[-1] != "/" and (tag == "link" or tag == "meta" or tag == "img" or tag == "hr" or tag == "br"):
			self.end_element(balise)

	def end_element(self, balise):
		"""Méthode invoquée lorsque le parser détecte une balise fermante."""
		# On met à jour la balise courante avec les données s'il y en a.
		if self.data != "":
			self.curElement.valeur = self.data
			self.data = ""
		# On repositionne le pointeur courant sur le père.
		self.curElement = self.curElement.parent



# Ouverture du fichier d'origine dans le parser Html.
#parser_xml = XmlFileParser("config.xml")
# Ecriture dans le fichier.
#parser_xml.save_as_html("test.htm")