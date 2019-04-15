import datetime
import math
import time
import random
import pprint
from collections import deque, Counter
import logging
import operator
from itertools import chain
from base_solver import BaseSolver

class CDCL(BaseSolver):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None, model_path=None):
        super(CDCL, self).__init__(formula, atomic_props, log_level, log_file, branching_heuristic, model_path)
        self.assignments, self.level_assignments = {}, {}
        self.implication_graph, self.level_forced_assign_var_map = {}, {}
        self.init_var_clause_map(atomic_props)
        self.newly_assigned_vars = []
        self.num_conflicts = 0
        self.branching_fn = self.choose_branching_heuristic(branching_heuristic)
    def choose_branching_heuristic(self, branching_heuristic):
        if branching_heuristic == "mvsids" or branching_heuristic == "cvsids":
            self.init_vsids()
            return self.heuristic_vsids
        return super(CDCL, self).choose_branching_heuristic(branching_heuristic)
    def init_vsids(self):
        self.var_activities = {}
        self.var_decided_vals = {}
        self.decay_val = 0.8
        self.decay_period = 1
        self.bonus_coeff = 1.2
        self.var_activities = dict(self.compute_jw_scores(self.formula))
        self.bonus_score = max(list(self.var_activities.values()))/2.0
    def heuristic_vsids(self, formula, assignments, k=1):
        remaining_var_activities = {}
        for var, activity in self.var_activities.items():
            if var not in self.assignments:
                remaining_var_activities[var] = activity
        return [x[0] for x in sorted(remaining_var_activities.items(), key=lambda x: x[1])][:-k]
    def get_assign_value_vsids(self, next_var):
        if next_var not in self.var_decided_vals:
            next_var_val = self.get_assign_value(next_var)
            self.var_decided_vals[next_var] = next_var_val
        else:
            next_var_val = self.var_decided_vals[next_var]
        return next_var_val
    def assign_next_var(self, formula, assignments, shortened=False):
        self.pick_branching_num += 1
        if shortened:
            formula = self.shorten_formula(formula, assignments)
        assert [] not in formula
        next_var = 0 if len(formula) == 0 else self.branching_fn(formula, assignments)[0]
        if next_var != 0:
            if self.branching_heuristic == "cvsids" or self.branching_heuristic == "mvsids":
                next_var_val = self.get_assign_value_vsids(next_var)
            else:
                next_var_val = self.get_assign_value(next_var)
        else:
            next_var_val = -1
        logging.debug("Assign {} next as {} at #{}".format(next_var, next_var_val, self.pick_branching_num))
        return next_var, next_var_val
    def set_log_level(self, log_level, log_file):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        if log_level == "DEBUG":
            print("Set log level to {}".format(log_level))
            if log_file:
                logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.DEBUG)
    def init_var_clause_map(self, atomic_props):
        self.hash_clause_map = {}
        self.lit_hash_map = {}
        self.clause_idx_hash_map = {}
        for i, clause in enumerate(self.formula):
            clause_hash = self.hash_clause(clause)
            self.hash_clause_map[clause_hash] = clause
            self.clause_idx_hash_map[i] = clause_hash
        for var in self.atomic_props:
            self.lit_hash_map[var] = []
            self.lit_hash_map[-var] = []
        for clause in self.formula:
            for lit in clause:
                self.lit_hash_map[lit].append(self.hash_clause(clause))
    def compute_ap_assignment_value(self, lit):
        return 1 if lit > 0 else 0
    def assign_var(self, var, level, value):
        if var in self.assignments:
            if self.assignments[var][0] != value: 
                return False
            return True
        self.assignments[var] = (value, level)
        if level not in self.level_assignments:
            self.level_assignments[level] = []
        self.level_assignments[level].append(var)
        return True
    def _force_assign_var(self, var, level, value):
        self.assign_var(var, level, value)
        self.level_forced_assign_var_map[level] = var
    def force_assign_var(self, level):
        logging.debug("Level {}".format(level))
        next_var, next_var_val = self.assign_next_var(self.formula, self.assignments, True)
        if next_var == 0:
            return True, next_var
        if level not in self.level_assignments:
            self.level_assignments[level] = []
        self._force_assign_var(next_var, level, next_var_val)
        return False, next_var
    def assign_pure_vars(self, level):
        if level-1 not in self.level_assignments:
            checking_vars = self.atomic_props
        else:
            last_assigned_vars = self.level_assignments[level-1]
            checking_vars = set()
            for var in last_assigned_vars:
                true_lit = var if self.assignments[var][0] > 0 else -var
                for clause in self.get_involved_clauses(true_lit):
                    checking_vars.union(set([abs(lit) for lit in clause]))
            checking_vars = list(checking_vars)
        for var in checking_vars:
            if var not in self.assignments:
                has_pos_lit = False
                for clause_hash in self.lit_hash_map[var]:
                    if self.check_clause_status_wrapper(clause_hash)[0] != "sat":
                        has_pos_lit = True
                if not has_pos_lit:
                    assignable = self.assign_var(var, level, 0)
                    if not assignable:
                        raise Exception("Pure var must be assignable")
                    self.update_newly_assigned_vars([var], False)
                    logging.debug("Assigning value 0 to {} from pure vars".format(var))
                    continue
                has_neg_lit = False
                for clause_hash in self.lit_hash_map[-var]:
                    if self.check_clause_status_wrapper(clause_hash)[0] != "sat":
                        has_neg_lit = True
                if not has_neg_lit:
                    assignable = self.assign_var(var, level, 1)
                    if not assignable:
                        raise Exception("Pure var must be assignable")
                    self.update_newly_assigned_vars([var], False)
                    logging.debug("Assigning value 1 to {} from pure vars".format(var))
    def assign_conflict_lit(self, clause, level):
        conflict_lit = 0
        for lit in clause:
            if self.assignments[abs(lit)][1] == level:
                conflict_lit = lit
                break
        if conflict_lit == 0:
            raise Exception("Conflict clause must have a lit assigned in conflict level.")
        logging.debug("Assign {} as conflict lit".format(conflict_lit))
        return conflict_lit
    def update_implication_graph(self, unassigned_lit, parents):
        if unassigned_lit in self.implication_graph:
            raise Exception("Unassigned lit {} already exists in implication graph.".format(unassigned_lit))
        self.implication_graph[unassigned_lit] = parents
    def update_newly_assigned_vars(self, vars, force):
        if force:
            self.newly_assigned_vars = vars
        else:
            for v in vars:
                if v not in self.newly_assigned_vars:
                    self.newly_assigned_vars = [v] + self.newly_assigned_vars
        logging.debug("Newly assigned vars {}".format(self.newly_assigned_vars))
    def get_involved_clauses(self, lit):
        return [self.hash_clause_map[h] for h in self.lit_hash_map[lit]]
    def check_clause_status_wrapper(self, clause_hash):
        start_time = datetime.datetime.now()
        res = self.check_clause_status(clause_hash)
        exec_time = (datetime.datetime.now() - start_time).total_seconds()
        self.check_clause_status_time += exec_time
        return res
    def check_clause_status(self, clause_hash):
        clause = self.hash_clause_map[clause_hash]
        clause_values = [self.compute_val(lit, self.assignments) for lit in clause]
        if 1 not in clause_values:  
            if -1 not in clause_values:
                logging.debug("Conflict detected in clause {}".format(clause))
                return "conflict", clause, 0
            if sum(clause_values) == -1:
                unassigned_lit = clause[clause_values.index(-1)]
                return "unit", clause, unassigned_lit
            return "unassaigned", [], 0
        return "sat", [], 0
    def deduce(self, level):
        while len(self.newly_assigned_vars) > 0:
            var = self.newly_assigned_vars.pop()
            true_lit = var if self.assignments[var][0] > 0 else -var
            false_lit = -true_lit
            logging.debug("Formula of newly assigned vars {}".format(self.get_involved_clauses(var)))
            for clause_hash in self.lit_hash_map[false_lit]:
                status, clause, unassigned_lit = self.check_clause_status_wrapper(clause_hash)
                if status == "conflict":
                    self.update_implication_graph(0, clause)
                    return True
                if status == "unit":
                    self.assign_lit_from_clause(unassigned_lit, clause, level)
                    self.update_implication_graph(unassigned_lit, [-lit for lit in clause if lit != unassigned_lit])
                    self.update_newly_assigned_vars([abs(unassigned_lit)], False)
        return False
    def assign_lit_from_clause(self, unassigned_lit, clause, level):
        assigned_value = 1 if unassigned_lit > 0 else 0
        var = abs(unassigned_lit)
        logging.debug("Assigning value {} to {} from {}".format(assigned_value, var, clause))
        self.assign_var(var, level, assigned_value)
    def get_learnt_clause(self, analysing_clause):
        return [-lit for lit in analysing_clause]
    def conflict_analyse(self, level):
        temp_level_lits_map = {}
        analysing_clause = [-lit for lit in self.implication_graph[0]]
        for lit in analysing_clause:
            lvl = self.assignments[abs(lit)][1]
            if lvl not in temp_level_lits_map:
                temp_level_lits_map[lvl] = []
            temp_level_lits_map[lvl].append(lit)
        while len(temp_level_lits_map[level]) > 1:
            logging.debug("Analysing {}".format(list(chain.from_iterable(temp_level_lits_map.values()))))
            next_lit = temp_level_lits_map[level][1] if abs(temp_level_lits_map[level][0]) == self.level_forced_assign_var_map[level] else temp_level_lits_map[level][0]
            for parent in self.implication_graph[next_lit]:
                parent_lvl = self.assignments[abs(parent)][1]
                if parent_lvl not in temp_level_lits_map:
                    temp_level_lits_map[parent_lvl] = []
                if -parent in temp_level_lits_map[parent_lvl]:
                    raise Exception("Learnt clause must not have 2 opposite lits")
                if parent not in temp_level_lits_map[parent_lvl]:
                    temp_level_lits_map[parent_lvl].append(parent)
            temp_level_lits_map[level].remove(next_lit)
            if self.branching_heuristic == "mvsids":
                self.var_activities[abs(next_lit)] += self.bonus_score
        learnt_clause = self.get_learnt_clause(list(chain.from_iterable(temp_level_lits_map.values())))
        levels = [self.assignments[abs(lit)][1] for lit in learnt_clause]
        backtrack_level = 0 if len(levels) < 2 else sorted(levels)[-2]
        logging.debug("Learning new clause {}, levels {}".format(learnt_clause, levels))
        logging.debug("Backtrack to level {}".format(backtrack_level))
        return learnt_clause, backtrack_level
    def backtrack(self, backtrack_level, current_level):
        forced_assign_var = self.level_forced_assign_var_map[backtrack_level] if backtrack_level != 0  else -1
        forced_assign_var_value = self.assignments[forced_assign_var][0] if backtrack_level != 0 else -1
        for level in range(backtrack_level, current_level+1):
            if level != 0:
                logging.debug("Clearing level {}".format(level))
                assigned_aps = self.level_assignments[level]
                for var in assigned_aps:
                    del self.assignments[var]
                    if var in self.implication_graph:
                        del self.implication_graph[var]
                    if -var in self.implication_graph:
                        del self.implication_graph[-var]
                del self.level_assignments[level]
                del self.level_forced_assign_var_map[level]
        del self.implication_graph[0]
        return forced_assign_var, forced_assign_var_value
    def update_learnt_clause(self, learnt_clause):
        clause_hash = self.hash_clause(learnt_clause)
        self.hash_clause_map[clause_hash] = learnt_clause
        self.clause_idx_hash_map[len(self.clause_idx_hash_map)] = clause_hash
        self.formula.append(learnt_clause)
        for lit in learnt_clause:
            self.lit_hash_map[lit].append(clause_hash)
        return clause_hash
    def update_var_activities(self, learnt_clause):
        if self.branching_heuristic == "cvsids":
            for lit in learnt_clause:
                self.var_activities[abs(lit)] += self.bonus_score
        logging.debug("Activity score: {}".format(self.var_activities))
        self.bonus_score *= math.ceil(self.bonus_coeff)
        if self.num_conflicts % self.decay_period == 0:
            for var in self.var_activities:
                self.var_activities[var] *= self.decay_val
            self.bonus_score *= math.ceil(self.decay_val)
    def solve_sat(self):
        self.level = 0
        sat = False
        while not sat:
            self.assign_pure_vars(self.level)
            conflict = self.deduce(self.level)
            if conflict:
                if self.level == 0:
                    sat = False
                    break
                self.num_conflicts += 1
                learnt_clause, backtrack_level = self.conflict_analyse(self.level)
                self.update_learnt_clause(learnt_clause)
                forced_assign_var, forced_assign_var_value = self.backtrack(backtrack_level, self.level)
                if backtrack_level != 0:
                    self._force_assign_var(forced_assign_var, backtrack_level, forced_assign_var_value)
                    self.update_newly_assigned_vars([forced_assign_var], True)
                else:
                    single_lit = learnt_clause[0]
                    self.assign_var(abs(single_lit), 0, 1 if single_lit > 0 else 0)
                    self.update_newly_assigned_vars([abs(single_lit)], True)
                self.level = backtrack_level
                if self.branching_heuristic == "cvsids" or self.branching_heuristic == "mvsids":
                    self.update_var_activities(learnt_clause)
            else:
                self.level += 1
                sat, next_var = self.force_assign_var(self.level)
                self.update_newly_assigned_vars([next_var], False)
        if sat:
            logging.debug("SAT")
        else:
            logging.debug("UNSAT")
        return sat