import argparse

from io import SatReader
from dpll import DPLL
from cdcl import CDCL
from simple_dpll import SimpleDPLL

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="sat-examples/sat1.cnf", help="SAT input")
    parser.add_argument("--log-level", type=str, default=None, help="Log level")
    parser.add_argument("--log-file", type=str, default="log.out", help="Log output")
    parser.add_argument("--solver-name", type=str, default="cdcl", help="Solver's name")

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
    sat_reader = SatReader(configs.input)
    cnf = sat_reader.read_input()
    solver_class = choose_solver(configs.solver_name)
    solver = solver_class(cnf.formula, [x+1 for x in range(cnf.num_props)], configs.log_level, configs.log_file)
    sat = solver.solve()
    if sat:
        print("SAT")
    else:
        print("UNSAT")

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    run_sat_solver(CONFIGS)