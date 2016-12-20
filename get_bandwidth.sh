#!/bin/bash

# Script de relevé de bande passante.
# Syntaxe : get_bandwidth.sh <pid_processus> <num_col>

path="$(readlink -f `dirname $0`)"
tail -n 1 $path/$1 | cut -d ":" -f $2
