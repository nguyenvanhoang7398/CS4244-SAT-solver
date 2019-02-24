import argparse

from io import SatReader
from solvers import BaselineDPLLSolver

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="sat-examples/sat1.cnf", help="SAT input")
    parser.add_argument("--output", type=str, default="output.txt", help="SAT output")

def run_sat_solver(configs):
    sat_reader = SatReader(configs.input)
    cnf = sat_reader.read_input()
    solver = BaselineDPLLSolver()
    result = solver.solve(cnf)
    print("Sat solver run in", result["time"])
    print(result["solution"])

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    run_sat_solver(CONFIGS)