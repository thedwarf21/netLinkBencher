#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import requests
import sys
import time
import ctypes

class DownloadFile:

	""" Thread chargé du bench de téléchargement descendant. """

	def __init__(self, url, directory, tps_exec):
		""" Constructeur. """
		self.url = url
		self.directory = directory
		libc = ctypes.cdll.LoadLibrary('libc.so.6')
		pid = libc.syscall(186)
		tps_exec = float(float(tps_exec) * 1000)		# Conversion des sec en ms

		# Boucle infinie (ou presque).
		print ("Processus en download", pid, "lancé.")
		elapsed = 0.0
		start = time.time()
		while elapsed < tps_exec:
			localFilename = self.url.split('/')[-1]
			with open(self.directory + '/' + localFilename, 'wb') as f:
				try:
					r = requests.get(self.url, stream=True)
					total_length = r.headers.get('content-length')
					dl = 0
					if total_length is None: # no content length header
						for chunk in r.iter_content(1024):
							dl += len(chunk)
							f.write(chunk)
					else:
						dl = total_length
						f.write(r.content)
				except ConnectionError as err:
					print ("Erreur requête DOWNLOAD : {0}".format(err))
			elapsed = time.time() - start
		print ("Le processus", pid, "s'est arrêté proprement.")

def main():
	if len(sys.argv) == 4:
		url = sys.argv[1]
		directory = sys.argv[2]
		tps_exec = sys.argv[3]
	else:
		print ("Syntaxe de la commande:", sys.argv[0], "<url> <local_dir> <temps_exec_en_sec>")

	dl = DownloadFile(url, directory, tps_exec)

if __name__ == "__main__":
	main()