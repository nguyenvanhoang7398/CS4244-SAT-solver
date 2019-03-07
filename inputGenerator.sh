#!/bin/sh

# $1 is the input name
# $2 variables
# $3 literals
# $4 clauses

# example for input: 1 150 3 650
# create file input1.cnf and file satis1.txt
uuid=$(uuidgen)
input_name="input${uuid}.cnf"
cnfgen -o $input_name randkcnf $2 $1 $3
output_name="./satis${uuid}.txt"
output=`cat $input_name | docker run --rm -i msoos/cryptominisat | tail -1`
touch $output_name
if [ "$output" = "s UNSATISFIABLE" ]
then
	echo "UNSATISFIABLE" > $output_name
else
	echo "SATISFIABLE" > $output_name
fi
