SAT solver for CS4244 project
=======================

## Setup

### Install cnfgen
```
pip install  [--user] cnfgen
```

### Install cryptominisat
[Follow these instructions to install cryptominisat python package](https://github.com/msoos/cryptominisat)

## CLI usage

### Edit `sat_solver.conf` for configs to be imported to scripts
```
# generating input configs
num_files=10
num_lits=3
num_vars=50
num_clauses=200
input_path=inputs
# experiment configs
solvers=("cdcl" "simple_dpll" "cryptosat")
heuristics=("random" "2clause")
applied_solvers=("cdcl")
log_level=DEBUG
output_dir=outputs
result_path=results.out
```

### Create inputs
```
./generate_inputs.sh
```
By default, inputs are stored at `./inputs`

### Run experiments
```
./run_experiments.sh
```
By default, outputs and experiment's results are stored at `./outputs` and `./results.out`

### Comparing the results of each solver to cryptominisat's
```
python compare_results.py
```

## Python usage
```
python sat_solver.py [--input <path-to-input>]
                     [--log-level DEBUG]
                     [--output <path-to-output>]
                     [--solver-name dpll|cdcl|simple_dpll|cryptosat]
                     [--branching-heuristic random|2clause]
```
