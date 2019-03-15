import argparse

from io import SatReader, SatWriter
from dpll import DPLL
from cdcl import CDCL
from simple_dpll import SimpleDPLL
import os

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="sat-examples/sat1.cnf", help="SAT input")
    parser.add_argument("--log-level", type=str, default=None, help="Log level")
    parser.add_argument("--output", type=str, default="output/", help="SAT output")
    parser.add_argument("--solver-name", type=str, default="cdcl", help="Solver's name")
    parser.add_argument("--branching-heuristic", type=str, default=None, help="Branching heuristic: random|2clause")

def choose_solver(solver_name):
    if solver_name == "cdcl":
        print("Use CDCL solver")
        return CDCL
    elif solver_name == "dpll":
        print("Use DPLL solver")
        return DPLL
    elif solver_name == "simple_dpll":
        print("Use simple DPLL solver")
        return SimpleDPLL
    raise ValueError("Unrecognised solver name")

def run_sat_solver(configs):
    if os.path.isdir(configs.input):
        run_sat_solver_multiple(configs)
    else:
        run_sat_solver_single(configs, configs.input)

def run_sat_solver_single(configs, input_path):
    sat_reader = SatReader()
    sat_writer = SatWriter()
    cnf = sat_reader.read_input(input_path)
    solver_class = choose_solver(configs.solver_name)
    input_name = extract_input_name(input_path)
    output_file = format_output_path(configs.output, input_name, ".out")
    log_file = format_output_path(configs.output, input_name, ".log")
    solver = solver_class(cnf.formula, [x+1 for x in range(cnf.num_props)], configs.log_level, log_file, configs.branching_heuristic)
    sat = solver.solve()
    sat_output = "SAT" if sat else "UNSAT"
    sat_writer.write_output(output_file, sat_output)

def run_sat_solver_multiple(configs):
    for input_name in os.listdir(configs.input):
        input_path = os.path.join(configs.input, input_name)
        run_sat_solver_single(configs, input_path)

def extract_input_name(input_path):
    return os.path.basename(input_path)

def format_output_path(output_folder, output_name, out_type):
    return os.path.join(output_folder, output_name + out_type)

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    run_sat_solver(CONFIGS)