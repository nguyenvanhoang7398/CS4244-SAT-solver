#!/bin/sh

# Config.txt contains
# input name
# literals
# variables
# clauses

# example for input: 1 3 150 650
# create input file and sati
# 
config_file="sat_solver.conf"
. ${config_file}

rm -r ${input_path}
mkdir -p ${input_path}
while [ ${num_files} != 0 ]
do
	uuid=$(uuidgen)
	input_name="${input_path}/input-${uuid}.cnf"
	cnfgen -o ${input_name} randkcnf ${num_lits} ${num_vars} ${num_clauses}
	num_files=$[$num_files-1]
done
