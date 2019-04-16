SAT solver for CS4244 project
=======================

## Setup

### Install cnfgen
```
pip install  [--user] cnfgen
```

### Install cryptominisat
[Follow these instructions to install cryptominisat python package](https://github.com/msoos/cryptominisat)

### Install python 3.7 packages
```
pip install -r requirements.txt
```

## CLI usage

### Edit `sat_solver.conf` for configs to be imported to scripts
```
# generating input configs
num_files=20
num_lits=3
num_vars=50
num_clauses=
input_path=inputs
# experiment configs
solvers=("dpll" "cdcl" "cdcl_wl")
# heuristics=("cvsids" "mvsids")
heuristics=("random" "2clause" "maxo" "moms" "mams" "jw" "up" "gup" "sup")
applied_solvers=("cdcl_wl")
models=("neural_network")
log_level=None
output_dir=outputs
result_path=results.out
```

### Create inputs
```
./generate_inputs.sh
```
By default, inputs are stored at `./inputs`

### Build and train Learning-to-assign models
```
python sat_ml.py
```
By default, models are stored at `./model_dir`

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
                     [--result  <path-to-result>]
                     [--solver-name dpll|cdcl|cdcl_wl]
                     [--branching-heuristic random|2clause|maxo|moms|mams|jw|up|gup|sup]
                     [--experiment-name <some-name>]
                     [--model-dir <path-to-ml-directory>]
                     [--model-name <name-of-model-to-load> neural_network|decision_tree|svm|random_forest]
```

## Quick Start
```
python sat_solver.py [--input <path-to-input>]
```
