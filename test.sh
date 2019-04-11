num_vars=30
num_clauses=`python -c "print int(4.258*${num_vars}+58.26*(${num_vars}**(-2.0/3)))"`
echo ${num_clauses}
