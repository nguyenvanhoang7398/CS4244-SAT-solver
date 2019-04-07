import argparse

import datetime
from io import SatReader, SatWriter
from dpll import DPLL
from cdcl import CDCL
from cdcl_wl import CDCL_WL
# from cryptosat import CryptoSat
import os

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="sat-examples/sat1.cnf", help="SAT input")
    parser.add_argument("--log-level", type=str, default=None, help="Log level")
    parser.add_argument("--output", type=str, default="output/", help="SAT output")
    parser.add_argument("--result", type=str, default="output/results.txt", help="Experiment results")
    parser.add_argument("--solver-name", type=str, default="cdcl", help="Solver's name")
    parser.add_argument("--branching-heuristic", type=str, default=None, help="Branching heuristic: random|2clause")
    parser.add_argument("--experiment-name", type=str, default=None, help="Experiment's name")
    
def choose_solver(solver_name):
    if solver_name == "cdcl":
        print("Use CDCL solver")
        return CDCL
    if solver_name == "cdcl_wl":
        print("Use CDCL Watched Literal solver")
        return CDCL_WL
    elif solver_name == "dpll":
        print("Use DPLL solver")
        return DPLL
    elif solver_name == "cryptosat":
        print("Use CryptoSat solver")
        return CryptoSat
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
    log_file = format_output_path(configs.output, input_name, ".log") if configs.log_level else None
    solver = solver_class(cnf.formula, [x+1 for x in range(cnf.num_props)], configs.log_level, log_file, configs.branching_heuristic)
    metric = solver.solve()
    sat_output = "SAT" if metric.sat else "UNSAT"
    sat_writer.write_output(output_file, sat_output)
    return metric

def run_sat_solver_multiple(configs):
    solver_metrics = []
    for input_name in os.listdir(configs.input):
        input_path = os.path.join(configs.input, input_name)
        solver_metric = run_sat_solver_single(configs, input_path)
        solver_metrics.append(solver_metric)
    write_metrics_to_output(configs, solver_metrics)

def write_metrics_to_output(configs, solver_metrics):
    seconds = [metric.exec_time for metric in solver_metrics]
    avg_seconds = sum(seconds) / float(len(seconds))
    pick_branching_nums = [metric.pick_branching_num for metric in solver_metrics]
    avg_pick_branching_nums = sum(pick_branching_nums) / float(len(pick_branching_nums))
    heuristic = configs.branching_heuristic if configs.branching_heuristic else ""
    experiment_name = configs.experiment_name if configs.experiment_name else configs.solver_name + "-" + heuristic
    with open(configs.result, "a") as f:
        f.write("-" * 10 + experiment_name + "-" * 10 + "\n")
        f.write("Average time:" + str(datetime.timedelta(seconds=avg_seconds)) + "\n")
        f.write("Average number of picking branching variables:" + str(avg_pick_branching_nums) + "\n")

def extract_input_name(input_path):
    return os.path.basename(input_path)

def format_output_path(output_folder, output_name, out_type):
    return os.path.join(output_folder, output_name + out_type)

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    run_sat_solver(CONFIGS)
