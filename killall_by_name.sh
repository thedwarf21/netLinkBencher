#!/bin/bash

# Script de kill d'un ensemble de processus par nom.
# Syntaxe killall_by_name.sh <nom>

for pid in "`ps -A | grep $1 | awk '{print $1}'`"
do 
	sudo kill $pid
done
