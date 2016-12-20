#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import requests
import math
import sys
import time
import socket
import signal
from threading import Thread

def main(contension, host, port, tps_exec):
	"""Méthode principale du script."""
	interval = 1 / 10
	start = time.time()
	loop_start = start
	elapsed = 0
	while tps_exec > elapsed:
		# Envoi.
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(1)
			s.connect((host, port))
			s.send(bytearray(round(1024 * contension / 10)))
			#with open("1k.bin", "rb") as f:
				#s.send(f.read())
			s.shutdown(socket.SHUT_RD)
		except socket.timeout:
			print ("Erreur du flux non saturant: timeout")
		except OSError as e:
			print ("Erreur du flux non saturant:", e)

		elapsed = time.time() - start
		loop_time = time.time() - loop_start
		if loop_time < interval * 1000:
			time.sleep(interval - (loop_time / 1000))
		loop_start = time.time()


if __name__ == "__main__":
	if len(sys.argv) < 5:
		print("Nombre d'arguments incorrect.\nSyntaxe:", sys.argv[0], "<contension> <hôte> <port> <temps_exécution>")
	else:
		contension = int(sys.argv[1])
		host = sys.argv[2]
		port = int(sys.argv[3])
		tps = math.floor(float(sys.argv[4]))

		main(contension, host, port, tps)
