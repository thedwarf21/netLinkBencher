#!/bin/bash

# Script de lancement de nethogs pour un processus.
# Syntaxe : launch_nethogs.sh <pid_processus>

path="$(readlink -f `dirname $0`)"
pid="$1"
fichier=$path/$pid
> $fichier
nethogs -t | awk '$1 ~ /\/'"$pid"'\// { print $2":"$3 >> "'"$fichier"'"; system("echo toto > /dev/null") }' &
