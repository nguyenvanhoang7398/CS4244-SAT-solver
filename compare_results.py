import os
from pprint import pprint

output_path="outputs/"
true_solver="output-dpll--"

result_map = {}
for solver in os.listdir(output_path):
    result_map[solver] = {}
    for output_file in os.listdir(os.path.join(output_path, solver)):
        if output_file.endswith('.cnf.out'):
            with open(os.path.join(output_path, solver, output_file), 'r') as f:
                result_map[solver][output_file] = f.readline()
errors = {}
error_rates = {}
for solver, result in result_map.items():
    errors[solver] = []
    for i, o in result.items():
        if o != result_map[true_solver][i]:
            errors[solver].append(i)
    error_rates[solver] = len(errors[solver])/float(len(result))
pprint("Detected errors:")
pprint(errors)
pprint("Error rates:")
pprint(error_rates)