SAT solver for CS4244 project
=======================

## Setup

### Install cnfgen
```
pip install  [--user] cnfgen
```

### Install docker
[Follow these instructions](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)

## CLI usage

### Create test cases
config.txt
[--num-file][--num-literal][--num-var][--num-clauses]

```
./inputGenerator.sh
```

```
python sat_solver.py [--input <path-to-input>]
                     [--log-level DEBUG]
                     [--solver-name dpll|cdcl|simple_dpll]
                     [--log-file <path-to-output-log]
```
