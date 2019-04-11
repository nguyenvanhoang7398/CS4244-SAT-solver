import numpy as np

def build_features(formula, var):
    # Ratio of pos/neg lit
    pos_neg_ratio = get_pos_neg_ratio(formula, var)
    mean_pos_lit, var_pos_lit = get_lit_clause_num_stats(formula, var)
    mean_neg_lit, var_neg_lit = get_lit_clause_num_stats(formula, -var)
    return np.array([pos_neg_ratio, mean_pos_lit, var_pos_lit, mean_neg_lit, var_neg_lit]).reshape(1, -1)

def get_lit_clause_num_stats(formula, lit):
    num_other_lits = [len(clause)-1 for clause in formula if lit in clause]
    return np.mean(num_other_lits), np.var(num_other_lits)

def get_pos_neg_ratio(formula, var):
    pos_num, neg_num = 0, 0
    for clause in formula:
        if var in clause:
            pos_num += 1
        elif -var in clause:
            neg_num += 1
    return float(pos_num)/neg_num