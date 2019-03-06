#!/bin/sh

# $1 is the input name
# $2 variables
# $3 literals
# $4 clauses

# example for input: 1 150 3 650
# create file input1.cnf and file satis1.txt
input_name="input${1}.cnf"
cnfgen -o $input_name randkcnf $3 $2 $4
output_name="./satis${1}.txt"
output=`cat $input_name | docker run --rm -i msoos/cryptominisat | tail -1`
touch $output_name
if [ "$output" = "s UNSATISFIABLE" ]
then
	echo "UNSATISFIABLE" > $output_name
else
	echo "SATISFIABLE" > $output_name
fi
