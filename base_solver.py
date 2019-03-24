import logging
import random
from collections import Counter

class BaseSolver(object):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None):
        self.formula = formula
        self.atomic_props = atomic_props
        self.set_log_level(log_level, log_file)
        self.branching_heuristic = branching_heuristic
    def assign_next_var(self, formula, assignments, shortened=False):
        branching_fn = self.choose_branching_heuristic()
        if shortened:
            formula = self.shorten_formula(formula, assignments)
        return 0 if len(formula) == 0 else branching_fn(formula, assignments)
    def compute_val(self, lit, assignments):
        if abs(lit) not in assignments:
            return -1
        elif assignments[abs(lit)][0] == 1:
            return 1 if lit > 0 else 0
        return 1 if lit < 0 else 0
    def shorten_formula(self, formula, assignment):
        shortened_formula = []
        for clause in formula:
            shortened_clause = []
            satisfied_clause = False
            for lit in clause:
                if self.compute_val(lit, assignment) == 1:
                    satisfied_clause = True
                    break
                if self.compute_val(lit, assignment) == -1:
                    shortened_clause.append(lit)
            if not satisfied_clause:
                shortened_formula.append(shortened_clause)
        return shortened_formula
    def choose_branching_heuristic(self):
        if self.branching_heuristic == "random":
            return self.heuristic_random
        if self.branching_heuristic == "2clause":
            return self.heuristic_2clause
        if self.branching_heuristic == "maxo":
            return self.heuristic_maxo
        if self.branching_heuristic == "moms":
            return self.heuristic_moms
        if self.branching_heuristic == "mams":
            return self.heuristic_mams
        if self.branching_heuristic == "jw":
            return self.heuristic_jw
        return self.heuristic_2clause
    def set_log_level(self, log_level, log_file):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        if log_level == "DEBUG":
            print("Set log level to {}".format(log_level))
            if log_file:
                logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.DEBUG)
    def get_var_counts(self, formula):
        var_counts = Counter()
        for clause in formula:
            for lit in clause:
                var = abs(lit)
                var_counts[var] = 0 if var not in var_counts else var_counts[var]
                var_counts[var] += 1
        return var_counts
    def heuristic_moms(self, formula, assignments):
        min_clause_size = min([len(clause) for clause in formula])
        min_formula = [clause for clause in formula if len(clause) == min_clause_size]
        return self.heuristic_maxo(min_formula, assignments)
    def heuristic_maxo(self, formula, assignments):
        var_counts = self.get_var_counts(formula)
        return var_counts.most_common(1)[0][0] if len(var_counts) > 1 else 0
    def heuristic_mams(self, formula, assignments):
        min_clause_size = min([len(clause) for clause in formula])
        min_formula = [clause for clause in formula if len(clause) == min_clause_size]
        moms_counts = self.get_var_counts(min_formula)
        maxo_counts = self.get_var_counts(formula)
        total_counts = Counter()
        for var, cnt in maxo_counts.items():
            total_cnt = cnt + moms_counts[var] if var in moms_counts else cnt
            total_counts[var] = total_cnt
        return total_counts.most_common(1)[0][0] if len(total_counts) > 1 else self.heuristic_random(formula, assignments)
    def heuristic_jw(self, formula, assignments):
        jw_scores = {}
        for clause in formula:
            for lit in clause:
                var = abs(lit)
                jw_scores[var] = jw_scores[var] if var in jw_scores else 0
                jw_scores[var] += 2**(-len(clause))
        if len(jw_scores) == 0:
            return 0
        max_score = max(jw_scores.values())
        max_score_vars = [var for var in jw_scores.keys() if jw_scores[var] == max_score]
        return random.choice(max_score_vars)
    def heuristic_2clause(self, formula, assignments):
        var_counts_2clause = {}
        for clause in formula:
            if len(clause) == 2:
                for lit in clause:
                    var = abs(lit) 
                    var_counts_2clause[var] = var_counts_2clause[var] if var in var_counts_2clause else 0
                    var_counts_2clause[var] += 1
        if len(var_counts_2clause) == 0:
            return self.heuristic_random(formula, assignments)
        max_count = max(var_counts_2clause.values())
        most_occuring_vars = [var for var in var_counts_2clause.keys() if var_counts_2clause[var] == max_count]
        return random.choice(most_occuring_vars)
    def heuristic_random(self, formula, assignments):
        assigned_vars = assignments.keys()
        unassigned_vars = [var for var in self.atomic_props if var not in assigned_vars]
        return 0 if len(unassigned_vars) == 0 else random.choice(unassigned_vars)