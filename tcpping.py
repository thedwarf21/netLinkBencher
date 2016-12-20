#!/usr/bin/python3.5
# -*-coding:utf-8 -*

import requests
import sys
import time
import socket
import signal
from threading import Thread
import ctypes

class TcpPing(Thread):

	""" Thread chargé du bench du ping TCP. """

	def __init__(self, host, port):
		""" Constructeur. """
		Thread.__init__(self)
		self.host = host
		self.port = port
		self.libc = ctypes.cdll.LoadLibrary('libc.so.6')
		self.running = True

	def run(self):
		""" Processus du thread. """
		while self.running:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(1)
			start = time.time()
			
			try:
				s.connect((self.host, int(self.port)))
				s.shutdown(socket.SHUT_RD)
			except socket.timeout:
				self.time_elapsed = -1
			except OSError as e:
				self.time_elapsed = -1

			self.time_elapsed = time.time() - start
			time.sleep(1 - (self.time_elapsed / 1000))
		print ("Le processus", self.getPID(), "s'est arrêté proprement.")

	def stop(self):
		""" Méthode de demande d'arrêt du processus. """
		self.running = False

	def getPID(self):
		""" Retourne le PID du thread. """
		return self.libc.syscall(186)

def main():
	if len(sys.argv) > 2:
		host = sys.argv[1]
		port = sys.argv[2]
	else:
		if len(sys.argv) > 1:
			host = sys.argv[1]
		else:
			host = input("Enter target host : ")
		url = input("Enter target port : ")

	thread_ping = TcpPing(host, port)
	thread_ping.start()
	thread_ping.join()
	print ("Latency:", thread_ping.time_elapsed * 1000, "ms")


if __name__ == "__main__":
	main()