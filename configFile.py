#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import sys
import time
from genericParser import XmlFileParser

class ConfigFile(XmlFileParser):

	"""Classe de parsing de fichier XML de configuration.

	Cette classe ouvre un fichier xml de configuration et en permet la manipulation 
	simplement en le mettant sous la forme d'un arbre (XmlFileParser).

	Elle permet ensuite par un ensemble de méthodes, d'interpréter le fichier de configuration.

	Attributs:
	  - stream : flux de données à parser. 							| GenericParser.FileParser.XmlFileParser
	  - data : variable temporaire pour les données entre balises. 	| GenericParser.FileParser.XmlFileParser
	  - niv_indent : niveau d'indentation. 							| FileParser.XmlFileParser
	  - top_comm : commentaire de haut de document. 				| XmlFileParser
	  - top_instruc : liste des instruction en haut du document. 	| XmlFileParser
	  - document : pointeur vers la balise maîtresse. 				| XmlFileParser
	  - curElement : pointeur vers le noeud de travail courant. 	| XmlFileParser

	"""

	def __init__(self, nom_fichier):
		"""Constructeur de la classe recevant le nom du fichier à mettre en forme."""
		XmlFileParser.__init__(self, nom_fichier)

	def getServeur(self):
		"""Méthode permettant de récupérer le serveur cible la config."""
		return self.document.getChild("init").getChild("serveur").valeur

	def getFichierDown(self):
		"""Méthode permettant de récupérer le nom du fichier à downloader."""
		return self.document.getChild("init").getChild("fichiers").getChild("download").valeur

	def getFichierUp(self):
		"""Méthode permettant de récupérer le nom du fichier à uploader."""
		return self.document.getChild("init").getChild("fichiers").getChild("upload").valeur

	def getFichierOutputPrefix(self):
		"""Méthode permettant de récupérer le préfixe de nom des fichiers de sortie."""
		return self.document.getChild("init").getChild("fichiers").getChild("output").valeur

	def getTypeFichierOutput(self):
		"""Méthode permettant de récupérer le type de fichier de sortie et donc l'extension."""
		return self.document.getChild("init").getChild("fichiers").getChild("output").properties["type"]

	def getPorts(self):
		"""Méthode permettant de récupérer les ports D1, D2 et D3."""
		d1 = self.document.getChild("init").getChild("ports").getChild("d1").valeur
		d2 = self.document.getChild("init").getChild("ports").getChild("d2").valeur
		d3 = self.document.getChild("init").getChild("ports").getChild("d3").valeur
		return d1, d2, d3

	def getInterStep(self):
		"""Méthode de récupération du nombre d'itérations entre deux étapes."""
		return self.document.getChild("init").getChild("inter").valeur

	def getBenchTime(self):
		"""Méthode de récupération du nombre total d'itérations."""
		return self.document.getChild("init").getChild("total").valeur

	def getLoopDuration(self):
		"""Méthode de récupération de la durée en millisecondes d'une boucle."""
		return self.document.getChild("init").getChild("loopDuration").valeur

	def getContension(self):
		"""Méthode de récupération de la taile en Ko/s des paquets envoyés par les flux non-saturants."""
		return self.document.getChild("init").getChild("contension").valeur

	def getStartTime(self):
		"""Méthode de récupération de l'heure de départ du bench."""
		return self.document.getChild("init").getChild("start_time").valeur

	def getNbTests(self):
		"""Méthode de récupération du nombre de tests."""
		return len(self.document.getChild("steps").children)

	def getNbSteps(self, index):
		"""Méthode de récupération du nombre d'étapes.
		
		Le premier indice est 0.
		
		"""
		tests = self.document.getChild("steps").children
		if index >= len(tests):
			return None
		else:
			return len(tests[index].children)

	def getTestSuffix(self, index):
		"""Méthode de récupération du préfixe du test.
		
		Le premier indice est 0.
		
		"""
		tests = self.document.getChild("steps").children
		if index >= len(tests):
			return None
		else:
			return tests[index].properties["suffix"]

	def getStepActions(self, numTest, numStep):
		"""Méthode de récupération des actions d'une étape.
		
		Le premier indice est 0 que ce soit pour numTest ou pour numStep.
		
		"""
		actions = list()
		tests = self.document.getChild("steps").children
		if numTest >= len(tests):
			return None
		else:
			steps = tests[numTest].children
			if numStep >= len(steps):
				return None
			else:
				for act in steps[numStep].children:
					actions.append(act.tag + " " + act.valeur)
				return actions

	def getStepInterCount(self, numTest, numStep):
		"""Méthode permettant de connaître le nombre d'intervalle d'application d'une étape.

		Par défaut (en l'absence de valeur) une étape dure un intervalle (n boucles définies dans inter).

		"""
		try:
			return int(self.document.getChild("steps").children[numTest].children[numStep].properties["count"])
		except KeyError:
			return 1


# Partie débug lancée si le fichier est lancé en tant que script.
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print ("Nombre d'argument invalide. Syntaxe:", sys.argv[0], "<fichier_de_conf>")
		exit(-1)

	print ("----------------------------------------------------------------------------")
	print ("Début du chargement du fichier de configuration de test.")
	print ("----------------------------------------------------------------------------")
	fichier_conf = ConfigFile(sys.argv[1])
	ports = fichier_conf.getPorts()
	nb_tests = fichier_conf.getNbTests()
	total_steps = 0
	nb_inter = 0
	i = 0
	while i < nb_tests:
		nb_steps = fichier_conf.getNbSteps(i)
		total_steps += nb_steps
		j = 0
		while j < nb_steps:
			nb_inter += fichier_conf.getStepInterCount(i, j)
			j += 1
		i += 1
	print ("Serveur :", fichier_conf.getServeur())
	print ("Fichier Down :", fichier_conf.getFichierDown())
	print ("Fichier Up :", fichier_conf.getFichierUp())
	print ("Préfixe fichiers de sortie :", fichier_conf.getFichierOutputPrefix())
	print ("Type du fichiers de sortie :", fichier_conf.getTypeFichierOutput())
	print ("Ports => d1:", ports[0], ", d2:", ports[1], ", d3:", ports[2])
	print ("Nombre de boucles par intervalle :", fichier_conf.getInterStep())
	print ("Nombre total de boucles :", fichier_conf.getBenchTime())
	print ("Durée par boucle (en ms) :", fichier_conf.getLoopDuration())
	print ("Quantité de données émises par les flux non-saturants (en ko/s) :", fichier_conf.getContension())
	print ("Départ différé à :", fichier_conf.getStartTime())
	print ("----------------------------------------------------------------------------")
	print ("Nombre de tests :", nb_tests)
	print ("Nombre total d'étapes :", total_steps)
	print ("Nombre d'intervalles :", nb_inter)
	print ("Nombre de boucles minimum pour ce test :", nb_inter * int(fichier_conf.getInterStep()))
	print ("Durée estimée du test :", int(fichier_conf.getBenchTime()) * int(fichier_conf.getLoopDuration()) / 1000 / 60, "minutes")
	print ("----------------------------------------------------------------------------")
	print ("|     Test     |  #  | Action  | Cible |")
	print ("----------------------------------------")
	i = 0
	while i < nb_tests:
		affichage_testname = False
		nb_steps = fichier_conf.getNbSteps(i)
		test_name = fichier_conf.getTestSuffix(i)
		nb_car_left = 12 - len(test_name)
		chaine0 = "| "
		cpt = 0
		bourrage = ""
		while cpt < nb_car_left // 2:
			bourrage += " "
			cpt += 1
		chaine0 += bourrage + test_name + bourrage
		if len(test_name) % 2 > 0:
			chaine0 += " "
		j = 0
		while j < nb_steps:
			affichage_num = False
			actions = fichier_conf.getStepActions(i, j)
			if j < 10:
				chaine1 = "|  " + str(j) + "  |"
			else:
				chaine1 = "| " + str(j) + "  |"
			for act in actions:
				act = act.split(" ")
				if act[0] == "start":
					chaine2 = "   +    | " + act[1] + " |"
				else:
					chaine2 = "   -    | " + act[1] + " |"

				if not affichage_testname:
					affichage_testname = True
				else:
					chaine0 = "|             "

				if not affichage_num:
					affichage_num = True
				else:
					chaine1 = "|     |"

				print (chaine0, chaine1, chaine2)
			j += 1
		i += 1
	print ("------------------------------------------------------------------")
	print ("Configuration chargée.")
	print ("------------------------------------------------------------------")
