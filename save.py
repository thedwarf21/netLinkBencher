#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import time

class Sauvegarde:
	"""Classe de sauvegarde (gère un fichier)."""

	def __init__(self, nom_fichier, type_fichier):
		"""Constructeur de la classe."""
		self.fichier = nom_fichier
		self.extension = type_fichier
		with open(self.fichier + "." + self.extension, "w") as fichier_sauvegarde:
			if self.extension == "json":
				fichier_sauvegarde.write("[")
			elif self.extension == "csv":
				fichier_sauvegarde.write("Date heure\tPing D1\tPing D2\tPing D3\tDown D1\tDown D2\tDown D3\tUp D1\tUp D2\tUp D3\n")

	def save(self, p_d1, p_d2, p_d3, d_d1, d_d2, d_d3, u_d1, u_d2, u_d3, is_last_line):
		"""Méthode permettant d'enregistrer une mesure."""
		with open(self.fichier + "." + self.extension, "a") as fichier_sauvegarde:
			if self.extension == "json":
				record = self.getJson(p_d1, p_d2, p_d3, d_d1, d_d2, d_d3, u_d1, u_d2, u_d3, is_last_line)
			elif self.extension == "csv":
				record = self.getCsv(p_d1, p_d2, p_d3, d_d1, d_d2, d_d3, u_d1, u_d2, u_d3, is_last_line)
			fichier_sauvegarde.write(record)

	def getJson(self, p_d1, p_d2, p_d3, d_d1, d_d2, d_d3, u_d1, u_d2, u_d3, is_last_line):
		"""Méthode générant une ligne au format JSON."""
		record = "{\"date_time\": \"" + self.getDateTime() + "\"" + \
				", \"P1\": " + p_d1 + ", \"P2\": " + p_d2 + ", \"P3\": " + p_d3 + \
				", \"D1\": " + d_d1 + ", \"D2\": " + d_d2 + ", \"D3\": " + d_d3 + \
				", \"U1\": " + u_d1 + ", \"U2\": " + u_d2 + ", \"U3\": " + u_d3 + "}"
		if is_last_line:
			return record + "]"
		else:
			return record + ",\n"

	def getCsv(self, p_d1, p_d2, p_d3, d_d1, d_d2, d_d3, u_d1, u_d2, u_d3, is_last_line):
		"""Méthode générant une ligne au format CSV."""
		record = self.getDateTime() + "\t" + p_d1 + "\t" + p_d2 + "\t" + p_d3 + "\t" + \
				self.dotToComma(d_d1) + "\t" + self.dotToComma(d_d2) + "\t" + self.dotToComma(d_d3) + "\t" + \
				self.dotToComma(u_d1) + "\t" + self.dotToComma(u_d2) + "\t" + self.dotToComma(u_d3)
		if not is_last_line:
			record += "\n"
		return record

	def dotToComma(self, string):
		"""Méthode transformant les points en virgules."""
		return string.replace(".", ",")

	def getDateTime(self):
		"""Retourne la date et heure courante au format YYYY-MM-DDTHH:mm:ss."""
		lt = time.localtime()
		year = str(lt.tm_year)
		month = str(lt.tm_mon)
		if len(month) < 2:
			month = "0" + month
		day = str(lt.tm_mday)
		if len(day) < 2:
			day = "0" + day
		hour = str(lt.tm_hour)
		if len(hour) < 2:
			hour = "0" + hour
		minutes = str(lt.tm_min)
		if len(minutes) < 2:
			minutes = "0" + minutes
		sec = str(lt.tm_sec)
		if len(sec) < 2:
			sec = "0" + sec
		return year + "-" + month + "-" + day + "T" + hour + ":" + minutes + ":" + sec