import argparse

import datetime
from io_utils import SatReader, SatWriter
from cdcl_wl import CDCL_WL
# from cryptosat import CryptoSat
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, make_scorer
from sklearn import svm
from sklearn.neural_network import MLPClassifier

from ml_utils import build_features

CONFIGS = None

def add_arguments(parser):
    """Build ArgumentParser."""
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--input", type=str, default="inputs", help="SAT input")
    parser.add_argument("--output", type=str, default="dataset_output/", help="SAT output")
    parser.add_argument("--model_dir", type=str, default="model_dir/", help="Model directory")

def run_sat_solver_single(configs, input_path):
    sat_reader = SatReader()
    cnf = sat_reader.read_input(input_path)
    solver_class = CDCL_WL
    solver = solver_class(cnf.formula, [x+1 for x in range(cnf.num_props)], branching_heuristic="jw")
    metric = solver.solve()
    sat_assignments = solver.assignments
    return metric, cnf.formula, sat_assignments

def extract_input_name(input_path):
    return os.path.basename(input_path)

def format_output_path(output_folder, output_name, out_type):
    return os.path.join(output_folder, output_name + out_type)

def build_raw_dataset(configs):
    datasets = []
    for input_name in os.listdir(configs.input):
        input_path = os.path.join(configs.input, input_name)
        solver_metric, formula, assignments = run_sat_solver_single(configs, input_path)
        if solver_metric.sat:
            datasets.append([formula, assignments])
    pickle.dump(datasets, open(os.path.join(configs.output, "raw_dataset.p"), "wb"))
    return datasets

def build_dataset(configs, raw_datasets):
    datasets = []
    for formula, assignments in raw_datasets:
        sub_datasets = build_dataset_from_formula_assignment(formula, assignments)
        datasets += sub_datasets
    pickle.dump(datasets, open(os.path.join(configs.output, "dataset.p"), "wb"))
    return datasets

def is_unpure(formula, var):
    flattened_formula = []
    for clause in formula:
        flattened_formula += clause
    return var in flattened_formula and -var in flattened_formula

def build_dataset_from_formula_assignment(formula, assignments):
    datasets = []
    vars = np.random.permutation(list(assignments.keys()))
    for var in vars:
        if is_unpure(formula, var):
            label = assignments[var][0]
            features = build_features(formula, var)
            formula = shorten_formula(formula, (var if label == 1 else -var))
            datasets.append([features, label])
    return datasets

def shorten_formula(formula, lit):
    shortened_formula = []
    for clause in formula:
        if -lit in clause:
            shortened_clause = []
            for l in clause:
                if l != -lit:
                    shortened_clause.append(l)
            shortened_formula.append(shortened_clause)
        elif lit not in clause:
            shortened_formula.append(clause)
    return shortened_formula

def train_sat_ml(datasets, configs):
    X, y = [], []
    for feature, label in datasets:
        X.append(feature[0])
        y.append(label)
    print(len(X), len(y))
    print("num pos", len([l for l in y if l == 1]))
    print("num neg", len([l for l in y if l == 0]))
    decision_tree_classifier(X, y, configs)
    random_forest_classifier(X, y, configs)
    svm_classifier(X, y, configs)
    neural_network_classifier(X, y, configs)

def decision_tree_classifier(X, y, configs):
    print("-" * 10 + "Decision tree" + "-" * 10)
    clf_dt = DecisionTreeClassifier(random_state=0)
    accuracy_scores = cross_val_score(clf_dt, X, y, scoring=make_scorer(accuracy_score), cv=10)
    f1_scores = cross_val_score(clf_dt, X, y, scoring=make_scorer(f1_score), cv=10)
    roc_auc_scores = cross_val_score(clf_dt, X, y, scoring=make_scorer(roc_auc_score), cv=10)
    print("Average accuracy: {}".format(sum(accuracy_scores)/len(accuracy_scores)))
    print("Average f1: {}".format(sum(f1_scores)/len(f1_scores)))
    print("Average roc auc: {}".format(sum(roc_auc_scores)/len(roc_auc_scores)))
    clf_dt.fit(X, y)
    pickle.dump(clf_dt, open(os.path.join(configs.model_dir, "decision_tree.p"), "wb"))

def random_forest_classifier(X, y, configs):
    print("-" * 10 + "Random forest" + "-" * 10)
    clf_rf = RandomForestClassifier(n_estimators=10, max_depth=3, random_state=0)
    accuracy_scores = cross_val_score(clf_rf, X, y, scoring=make_scorer(accuracy_score), cv=10)
    f1_scores = cross_val_score(clf_rf, X, y, scoring=make_scorer(f1_score), cv=10)
    roc_auc_scores = cross_val_score(clf_rf, X, y, scoring=make_scorer(roc_auc_score), cv=10)
    print("Average accuracy: {}".format(sum(accuracy_scores)/len(accuracy_scores)))
    print("Average f1: {}".format(sum(f1_scores)/len(f1_scores)))
    print("Average roc auc: {}".format(sum(roc_auc_scores)/len(roc_auc_scores)))
    clf_rf.fit(X, y)
    pickle.dump(clf_rf, open(os.path.join(configs.model_dir, "random_forest.p"), "wb"))

def svm_classifier(X, y, configs):
    print("-" * 10 + "SVM" + "-" * 10)
    clf_svm = svm.SVC(gamma="scale")
    accuracy_scores = cross_val_score(clf_svm, X, y, scoring=make_scorer(accuracy_score), cv=10)
    f1_scores = cross_val_score(clf_svm, X, y, scoring=make_scorer(f1_score), cv=10)
    roc_auc_scores = cross_val_score(clf_svm, X, y, scoring=make_scorer(roc_auc_score), cv=10)
    print("Average accuracy: {}".format(sum(accuracy_scores)/len(accuracy_scores)))
    print("Average f1: {}".format(sum(f1_scores)/len(f1_scores)))
    print("Average roc auc: {}".format(sum(roc_auc_scores)/len(roc_auc_scores)))
    clf_svm.fit(X, y)
    pickle.dump(clf_svm, open(os.path.join(configs.model_dir, "svm.p"), "wb"))

def neural_network_classifier(X, y, configs):
    print("-" * 10 + "Neural Network" + "-" * 10)
    clf_nn = MLPClassifier(solver='lbfgs', alpha=1e-5,
                           hidden_layer_sizes=(15, 2), random_state=0)
    accuracy_scores = cross_val_score(clf_nn, X, y, scoring=make_scorer(accuracy_score), cv=10)
    f1_scores = cross_val_score(clf_nn, X, y, scoring=make_scorer(f1_score), cv=10)
    roc_auc_scores = cross_val_score(clf_nn, X, y, scoring=make_scorer(roc_auc_score), cv=10)
    print("Average accuracy: {}".format(sum(accuracy_scores)/len(accuracy_scores)))
    print("Average f1: {}".format(sum(f1_scores)/len(f1_scores)))
    print("Average roc auc: {}".format(sum(roc_auc_scores)/len(roc_auc_scores)))
    clf_nn.fit(X, y)
    pickle.dump(clf_nn, open(os.path.join(configs.model_dir, "neural_network.p"), "wb"))

if __name__ == "__main__":
    solver_parser = argparse.ArgumentParser()
    add_arguments(solver_parser)
    CONFIGS, unparsed = solver_parser.parse_known_args()
    raw_datasets = build_raw_dataset(CONFIGS)
    datasets = build_dataset(CONFIGS, raw_datasets)
    # datasets = pickle.load(open(os.path.join(CONFIGS.output, "dataset.p"), "rb"))
    train_sat_ml(datasets, CONFIGS)