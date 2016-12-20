#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import requests
import sys
import time
import os
import ctypes

class UploadFile():

	""" Thread chargé du bench de téléchargement ascendant. """

	def __init__(self, file_name, url, tps_exec):
		""" Constructeur. """
		self.file_name = file_name
		self.url = url
		libc = ctypes.cdll.LoadLibrary('libc.so.6')
		pid = libc.syscall(186)
		tps_exec = float(float(tps_exec) * 1000)	# Conversion des sec en ms

		# Boucle infinie (ou presque).
		print ("Processus en upload", pid, "lancé.")
		elapsed = 0.0
		start = time.time()
		while elapsed < tps_exec:
			files = {'file': open(self.file_name, 'rb')}
			file_size = os.path.getsize(self.file_name)
			try:
				r = requests.post(self.url, files=files, data={})
			except ConnectionError as err:
					print ("Erreur requête UPLOAD : {0}".format(err))
			elapsed = time.time() - start
		print ("Le processus", pid, "s'est arrêté proprement.")

def main():
	if len(sys.argv) == 4:
		file_name = sys.argv[1]
		url = sys.argv[2]
		tps_exec = sys.argv[3]
	else:
		print ("Syntaxe :", sys.argv[0], "<file_name> <url> <tps_exec>")

	up = UploadFile(file_name, url, tps_exec)

if __name__ == "__main__":
	main()