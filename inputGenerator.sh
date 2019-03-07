#!/bin/sh

# Config.txt contains
# input name
# literals
# variables
# clauses

# example for input: 1 3 150 650
# create input file and sati
# 
config_file_name="config.txt"
read num_file num_literal num_var num_clauses < $config_file_name

rm -r input
rm -r satis
mkdir -p input
mkdir -p satis

while [ $num_file != 0 ]
do
	uuid=$(uuidgen)
	input_name="./input/input${uuid}.cnf"
	cnfgen -o $input_name randkcnf $num_literal $num_var $num_clauses
	output_name="./satis/satis${uuid}.txt"
	output=`cat $input_name | docker run --rm -i msoos/cryptominisat | tail -1`
	touch $output_name
	if [ "$output" = "s UNSATISFIABLE" ]
	then
		echo "UNSAT" > $output_name
	else
		echo "SAT" > $output_name
	fi
	num_file=`expr $num_file - 1`
done
