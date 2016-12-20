#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import os
import sys
import signal
import time
import subprocess
from tcpping import TcpPing
from save import Sauvegarde
from configFile import ConfigFile

def main(fichier_de_conf):

	"""Programme principal de benchmark des liens réseaux permettant de valider la QoS."""
	
	dir_path = os.path.dirname(os.path.abspath(__file__))
	os.chdir(dir_path)

	# Initialisation: depuis le fichier.
	conf = ConfigFile(fichier_de_conf)
	ports = conf.getPorts()
	serveur = conf.getServeur()
	fichier_dl = conf.getFichierDown()
	fichier_up = conf.getFichierUp()
	fichier_out_pre = conf.getFichierOutputPrefix()
	type_fichier = conf.getTypeFichierOutput()
	contension = conf.getContension()
	start_time = conf.getStartTime()
	inter_step = int(conf.getInterStep())
	bench_time = int(conf.getBenchTime())
	interval = int(conf.getLoopDuration())

	# Départ différé.
	while time.strftime("%H:%M") != start_time:
		pass

	print("Démarrage du script...")

	# Initialisation: le reste.
	nb_inter_left_to_do = 1
	num_test = 0
	num_etape = 0
	nb_steps_in_test = conf.getNbSteps(num_test)
	fichier_out = fichier_out_pre + "_" + conf.getTestSuffix(num_test)
	i = 0
	start = 0
	pid_dl, pid_up = [0, 0, 0], [0, 0, 0]
	down1, down2, down3 = "0", "0", "0"
	up1, up2, up3 = "0", "0", "0"
	running = [False, False, False, False, False, False]
	thread_ping1 = TcpPing(serveur, ports[0])
	thread_ping2 = TcpPing(serveur, ports[1])
	thread_ping3 = TcpPing(serveur, ports[2])
	thread_ping1.start()
	thread_ping2.start()
	thread_ping3.start()
	start = time.time()

	# Fichier de sortie.
	sauvegarde = Sauvegarde(fichier_out, type_fichier)
	print ("Création du fichier", fichier_out + "." + type_fichier)

	# Boucle principale.
	while i < bench_time:

		# Détection changement d'étape.
		if i > 0 and i % inter_step == 0:
			nb_inter_left_to_do -= 1
			if nb_inter_left_to_do == 0:
				actions = conf.getStepActions(num_test, num_etape)
				nb_inter_left_to_do = conf.getStepInterCount(num_test, num_etape)
				num_etape += 1

				# Détection changement de test.
				if num_etape >= nb_steps_in_test:
					num_test += 1
					num_etape = 0
					nb_steps_in_test = conf.getNbSteps(num_test)
					if nb_steps_in_test is not None:
						fichier_out = fichier_out_pre + "_" + conf.getTestSuffix(num_test)
						sauvegarde = Sauvegarde(fichier_out, type_fichier)
						print ("Création du fichier", fichier_out + "." + type_fichier)
				if actions is not None:
					for act in actions:
						act = act.split(" ")
						directive = act[0]
						args = act[1].split("_")
						temps = (bench_time - i) * (interval / 1000)
						idx = int(args[1][1]) - 1 # d1 -> 0, d2 -> 1, d3 -> 2
						if directive == "start":
							url = "http://" + serveur + ":" + ports[idx]
							if args[0] == "dl":
								pid_dl[idx] = subprocess.Popen(["./download.py", url + "/" + fichier_dl, ".", str(temps)]).pid
								subprocess.call(["./launch_nethogs.sh", str(pid_dl[idx])])
								running[idx] = True
							elif args[0] == "up":
								pid_up[idx] = subprocess.Popen(["./upload.py", fichier_up, url, str(temps)]).pid
								subprocess.call(["./launch_nethogs.sh", str(pid_up[idx])])
								running[idx + 3] = True
							else: # args[0] == "ns" -> non-saturant.
								pid_up[idx] = subprocess.Popen(["./flux_non_saturant.py", contension, serveur, ports[0], str(temps)]).pid
								subprocess.call(["./launch_nethogs.sh", str(pid_up[idx])])
								running[idx + 3] = True
						else: # directive == "stop"
							if args[0] == "dl":
								killProcess(pid_dl[idx])
								running[idx] = False
							else: # args[0] == "up" or args[0] == "ns"
								killProcess(pid_up[idx])
								running[idx + 3] = False

		# Calcul temps restant avant fin de l'itération puis attente jusque là.
		temps_restant = interval - (time.time() - start)
		if temps_restant > 0:
			time.sleep(temps_restant / 1000)
		
		# On redémarre le chrono pour la seconde suivante.
		start = time.time()

		# Relevé et sauvegarde des valeurs.
		p1 = str(thread_ping1.time_elapsed * 1000).split(".")[0]
		p2 = str(thread_ping2.time_elapsed * 1000).split(".")[0]
		p3 = str(thread_ping3.time_elapsed * 1000).split(".")[0]
		if running[0] is True:
			down1 = commande(["./get_bandwidth.sh", str(pid_dl[0]), "2"])
			if down1 == "":
				down1 = "0"
		else:
			down1 = "0"
		if running[1] is True:
			down2 = commande(["./get_bandwidth.sh", str(pid_dl[1]), "2"])
			if down2 == "":
				down2 = "0"
		else:
			down2 = "0"
		if running[2] is True:
			down3 = commande(["./get_bandwidth.sh", str(pid_dl[2]), "2"])
			if down3 == "":
				down3 = "0"
		else:
			down3 = "0"
		if running[3] is True:
			up1 = commande(["./get_bandwidth.sh", str(pid_up[0]), "1"])
			if up1 == "":
				up1 = "0"
		else:
			up1 = "0"
		if running[4] is True:
			up2 = commande(["./get_bandwidth.sh", str(pid_up[1]), "1"])
			if up2 == "":
				up2 = "0"
		else:
			up2 = "0"
		if running[5] is True:
			up3 = commande(["./get_bandwidth.sh", str(pid_up[2]), "1"])
			if up3 == "":
				up3 = "0"
		else:
			up3 = "0"

		sauvegarde.save(p1, p2, p3, down1, down2, down3, up1, up2, up3, (i == bench_time - 1))
		i += 1

	# Fin du bench : arrêt des processus et suppression des fichiers.
	thread_ping1.stop()
	thread_ping2.stop()
	thread_ping3.stop()

	# Processus Nethogs
	subprocess.call(["./killall_by_name.sh", "nethogs"])

	# Processus download.py
	for pid in pid_dl:
		killProcess(pid)

	# Processus upload.py
	for pid in pid_up:
		killProcess(pid)


def killProcess(pid):
	"""Fonction permettant de tuer un processus tout en supprimant son fichier de log.

	Cette fonction est réservée aux processus de download et upload 
	car ils génèrent des fichiers à leur nom.

	"""
	try:
		os.kill(pid, signal.SIGKILL)
		print ("Processus", pid, "arrêté avec succès.")
	except ProcessLookupError:
		print ("Processus", pid, "déjà arrêté.")
	subprocess.call(["rm", str(pid)])


def commande(list_args):
	"""Fonction permettant de récupérer le résultat d'une commande."""
	return subprocess.check_output(list_args).decode().split("\n")[0]


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print ("Erreur: paramètre manquant.", sys.argv[0], "<fichier_de_conf>")
	else:
		main(sys.argv[1])