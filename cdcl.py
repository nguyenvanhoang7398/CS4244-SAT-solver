import datetime
import time
import random
import pprint
from collections import deque, Counter
import logging
import operator
from itertools import chain
from base_solver import BaseSolver

class CDCL(BaseSolver):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None):
        super(CDCL, self).__init__(formula, atomic_props, log_level, log_file, branching_heuristic)
        self.assignments, self.level_assignments = {}, {}
        self.implication_graph, self.level_forced_assign_var_map = {}, {}
    def set_log_level(self, log_level, log_file):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        if log_level == "DEBUG":
            print("Set log level to {}".format(log_level))
            if log_file:
                logging.basicConfig(filename=log_file, filemode='w', level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.DEBUG)
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
    def assign_unit_clause(self):
        for clause in self.formula:
            if len(clause) == 1:
                lit = clause[0]
                assignable = self.assign_var(abs(lit), 0, self.compute_ap_assignment_value(lit))
                if not assignable:
                    return False
        return True
    def _force_assign_var(self, var, level, value):
        self.assign_var(var, level, value)
        self.level_forced_assign_var_map[level] = var
    def force_assign_var(self, level):
        next_var = self.assign_next_var(self.formula, self.assignments, True)
        if next_var == 0:
            return True
        logging.debug("Force assign {} as 1 at level {}".format(next_var, level))
        if level not in self.level_assignments:
            self.level_assignments[level] = []
        self._force_assign_var(next_var, level, 1)
        return False    
    def assign_pure_vars(self):
        lit_counts = {}
        for clause in self.formula:
            for lit in clause:
                lit_counts[lit] = 0 if lit not in lit_counts else lit_counts[lit]
                lit_counts[lit] += 1
        for lit, _ in lit_counts.items():
            if -lit not in lit_counts:
                assignable = self.assign_var(abs(lit), 0, self.compute_ap_assignment_value(lit))
                if not assignable:
                    raise Exception("Pure var must be assignable")
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
    def deduce(self, level):
        new_lit_assigned = True
        while new_lit_assigned:
            new_lit_assigned = False
            for clause in self.formula:
                clause_values = [self.compute_val(lit, self.assignments) for lit in clause]
                if 1 in clause_values:
                    continue
                if -1 not in clause_values:
                    logging.debug("Conflict detected in clause {}".format(clause))
                    # conflict_lit = self.assign_conflict_lit(clause, level)
                    self.update_implication_graph(0, clause)
                    return True
                if sum(clause_values) == -1:
                    unassigned_lit = clause[clause_values.index(-1)]
                    self.assign_lit_from_clause(unassigned_lit, clause, level)
                    self.update_implication_graph(unassigned_lit, [-lit for lit in clause if lit != unassigned_lit])
                    new_lit_assigned = True
                    break
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
    def solve(self):
        self.assign_pure_vars()
        level = 0
        all_assigned = False
        sat = True
        while not all_assigned:
            if level == 0:
                unit_assignable = self.assign_unit_clause()
                if not unit_assignable:
                    sat = False
                    break
                conflict = self.deduce(level)
                if conflict:
                    sat = False
                    break
                level += 1
                all_assigned = self.force_assign_var(level)
            else:
                conflict = self.deduce(level)
                if conflict:
                    learnt_clause, backtrack_level = self.conflict_analyse(level)
                    self.formula = [learnt_clause] + self.formula
                    forced_assign_var, forced_assign_var_value = self.backtrack(backtrack_level, level)
                    if backtrack_level != 0:
                        self._force_assign_var(forced_assign_var, backtrack_level, forced_assign_var_value)
                    level = backtrack_level
                else:
                    level += 1
                    all_assigned = self.force_assign_var(level)
        if sat:
            logging.debug("SAT")
        else:
            logging.debug("UNSAT")
        return sat