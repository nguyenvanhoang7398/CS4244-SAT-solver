import logging
import random
from collections import Counter
import datetime
from metrics import Metrics

class BaseSolver(object):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None):
        self.formula = formula
        self.atomic_props = atomic_props
        self.set_log_level(log_level, log_file)
        self.branching_heuristic = branching_heuristic
        self.pick_branching_num = 0
    def assign_next_var(self, formula, assignments, shortened=False):
        self.pick_branching_num += 1
        branching_fn = self.choose_branching_heuristic()
        if shortened:
            formula = self.shorten_formula(formula, assignments)
        return 0 if len(formula) == 0 else branching_fn(formula, assignments)[0]
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
        if self.branching_heuristic == "up":
            return self.heuristic_up
        if self.branching_heuristic == "gup":
            return self.heuristic_gup
        if self.branching_heuristic == "sup":
            return self.heuristic_sup
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
    def heuristic_moms(self, formula, assignments, k=1):
        min_clause_size = min([len(clause) for clause in formula])
        min_formula = [clause for clause in formula if len(clause) == min_clause_size]
        return self.heuristic_maxo(min_formula, assignments, k)
    def heuristic_maxo(self, formula, assignments, k=1):
        var_counts = self.get_var_counts(formula)
        return [s[0] for s in var_counts.most_common(k)]
    def heuristic_mams(self, formula, assignments, k=1):
        min_clause_size = min([len(clause) for clause in formula])
        min_formula = [clause for clause in formula if len(clause) == min_clause_size]
        moms_counts = self.get_var_counts(min_formula)
        maxo_counts = self.get_var_counts(formula)
        total_counts = Counter()
        for var, cnt in maxo_counts.items():
            total_cnt = cnt + moms_counts[var] if var in moms_counts else cnt
            total_counts[var] = total_cnt
        return [s[0] for s in total_counts.most_common(k)]
    def heuristic_jw(self, formula, assignments, k=1):
        jw_scores = Counter()
        for clause in formula:
            for lit in clause:
                var = abs(lit)
                jw_scores[var] = jw_scores[var] if var in jw_scores else 0
                jw_scores[var] += 2**(-len(clause))
        return [s[0] for s in jw_scores.most_common(k)]
    def heuristic_2clause(self, formula, assignments, k=1):
        var_counts_2clause = Counter()
        for clause in formula:
            if len(clause) == 2:
                for lit in clause:
                    var = abs(lit) 
                    var_counts_2clause[var] = var_counts_2clause[var] if var in var_counts_2clause else 0
                    var_counts_2clause[var] += 1
        return self.heuristic_random(formula, assignments) if len(var_counts_2clause) == 0 else [s[0] for s in var_counts_2clause.most_common(k)]
    def resolve_by_lit(self, formula, lit):
        resolved_formula = []
        for clause in formula:
            if -lit in clause:
                resolved_clause = [literal for literal in clause if literal != -lit]
                if len(resolved_clause) == 0:
                    return resolved_formula, [lit], True
                resolved_formula.append(resolved_clause)
            elif lit not in clause:
                resolved_formula.append(clause)
        return resolved_formula, [lit], False 
    def get_num_unit_propagation(self, formula, lit):
        num_unit_propagations = 0
        resolving_lits = [lit]
        resolved_formula = formula
        result_code = 0
        while len(resolving_lits) > 0:
            resolving_lit = resolving_lits.pop()
            resolved_formula, _, unsat = self.resolve_by_lit(resolved_formula, resolving_lit)
            if unsat:
                result_code = -1
                break
            if len(resolved_formula) == 0:
                result_code = 1
                break
            unit_lits = self.get_unit_lits(resolved_formula)
            num_unit_propagations += len(unit_lits)
            resolving_lits = unit_lits + resolving_lits
            resolving_lits = list(set(resolving_lits))
        return num_unit_propagations, result_code
    def get_unit_lits(self, formula):
        return [clause[0] for clause in formula if len(clause) == 1]
    def heuristic_up(self, formula, assignments, k=1):
        assigned_vars = assignments.keys()
        unassigned_vars = [var for var in self.atomic_props if var not in assigned_vars]
        return self._heuristic_up(formula, unassigned_vars, k)
    def _heuristic_up(self, formula, vars, k=1):
        var_up_map = Counter()
        for var in vars:
            num_up_from_var, _ = self.get_num_unit_propagation(formula, var)
            num_up_from_neg_var, _ = self.get_num_unit_propagation(formula, -var)
            var_up_map[var] = num_up_from_var + num_up_from_neg_var            
        return [s[0] for s in var_up_map.most_common(k)]
    def heuristic_gup(self, formula, assignments, k=1):
        assigned_vars = assignments.keys()
        unassigned_vars = [var for var in self.atomic_props if var not in assigned_vars]
        var_up_map = Counter()
        for var in unassigned_vars:
            num_up_from_var, status_code = self.get_num_unit_propagation(formula, var)
            if status_code != 0:
                return [var]
            num_up_from_neg_var, status_code = self.get_num_unit_propagation(formula, -var)
            if status_code != 0:
                return [var]
            var_up_map[var] = num_up_from_var + num_up_from_neg_var
        return [s[0] for s in var_up_map.most_common(k)]
    def heuristic_sup(self, formula, assignments, k=4):
        top_k_maxo = self.heuristic_maxo(formula, assignments, k)
        top_k_moms = self.heuristic_moms(formula, assignments, k)
        top_k_mams = self.heuristic_mams(formula, assignments, k)
        top_k_jw = self.heuristic_jw(formula, assignments, k)
        top_k = [x[0] for x in Counter(top_k_maxo + top_k_moms + top_k_mams + top_k_jw).most_common(k)]
        return self._heuristic_up(formula, top_k)
    def heuristic_random(self, formula, assignments):
        assigned_vars = assignments.keys()
        unassigned_vars = [var for var in self.atomic_props if var not in assigned_vars]
        return [random.choice(unassigned_vars)]
    def heuristic_ordered(self, formula, assignments):
        for var in self.atomic_props:
            if var not in assignments:
                return [var]
        return [0]
    def solve_sat(self):
        return random.choice([True, False])
    def solve(self):
        start_time = datetime.datetime.now()
        sat = self.solve_sat()
        exec_time = (datetime.datetime.now() - start_time).total_seconds()
        pick_branching_num = self.pick_branching_num
        return Metrics(sat, exec_time, pick_branching_num)