import argparse

from io import SatReader
from dpll import DPLL
from cdcl import CDCL

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="sat-examples/sat1.cnf", help="SAT input")
    parser.add_argument("--output", type=str, default="output.txt", help="SAT output")
    parser.add_argument("--solver-name", type=str, default="dpll", help="Name of the solver")

def run_sat_solver(configs):
    sat_reader = SatReader(configs.input)
    cnf = sat_reader.read_input()
    # solver = DPLL()
    # assignments, unsat, elapse = solver.solve(cnf)
    # if unsat:
    #     print("UNSAT")
    # else:
    #     print("SAT with assignments", assignments)
    solver = CDCL(cnf.formula, [x+1 for x in range(cnf.num_props)])
    solver.solve()

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    run_sat_solver(CONFIGS)