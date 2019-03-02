import datetime
import time
import random
import pprint
from collections import deque
import logging

class CDCL(object):
    def __init__(self, formula, atomic_props, log_level=None):
        self.formula = formula
        self.atomic_props = atomic_props
        self.debug = False
        self.assignments, self.level_assignments = {}, {}
        self.implication_graph, self.level_forced_assign_ap_map = {}, {}
        self.set_log_level(log_level)
    def set_log_level(self, log_level):
        if log_level == "DEBUG":
            print("Set log level to {}".format(log_level))
            logging.basicConfig(level=logging.DEBUG)
    def compute_ap_assignment_value(self, lit):
        return 1 if lit > 0 else 0
    def assign_ap(self, ap, level, value):
        if ap in self.assignments:
            if self.assignments[ap][0] != value: 
                return False
            return True
        self.assignments[ap] = (value, level)
        if level not in self.level_assignments:
            self.level_assignments[level] = []
        self.level_assignments[level].append(ap)
        return True
    def assign_unit_clause(self):
        for clause in self.formula:
            if len(clause) == 1:
                lit = clause[0]
                assignable = self.assign_ap(abs(lit), 0, self.compute_ap_assignment_value(lit))
                if not assignable:
                    return False
        return True
    def ordered_assign_ap(self):
        for ap in self.atomic_props:
            if ap not in self.assignments:
                return ap
        return 0
    def _force_assign_ap(self, ap, level, value):
        self.assign_ap(ap, level, value)
        self.level_forced_assign_ap_map[level] = ap
    def force_assign_ap(self, level):
        next_ap = self.ordered_assign_ap()
        if next_ap == 0:
            return True
        logging.debug("Force assign {} as 1 at level {}".format(next_ap, level))
        if level not in self.level_assignments:
            self.level_assignments[level] = []
        self._force_assign_ap(next_ap, level, 1)
        return False    
    def assign_pure_aps(self):
        lit_counts = {}
        for clause in self.formula:
            for lit in clause:
                lit_counts[lit] = 0 if lit not in lit_counts else lit_counts[lit]
                lit_counts[lit] += 1
        for lit, _ in lit_counts.items():
            if -lit not in lit_counts:
                assignable = self.assign_ap(abs(lit), 0, self.compute_ap_assignment_value(lit))
                if not assignable:
                    raise Exception("Pure ap must be assignable")
    def compute_val(self, lit):
        if abs(lit) not in self.assignments:
            return -1
        elif self.assignments[abs(lit)][0] == 1:
            return 1 if lit > 0 else 0
        return 1 if lit < 0 else 0
    def uniform_assign_conflict_lit(self, clause):
        return random.choice(clause)
    def assign_conflict_lit(self, clause):
        conflict_lit = self.uniform_assign_conflict_lit(clause)
        logging.debug("Assign {} as conflict lit".format(conflict_lit))
        return conflict_lit
    def update_implication_graph(self, unassigned_lit, parents):
        if unassigned_lit in self.implication_graph:
            raise Exception("Unassigned lit {} already exists in implication graph.".format(unassigned_lit))
        self.implication_graph[unassigned_lit] = parents
    def propagate_assignments(self, level):
        new_lit_assigned = True
        while new_lit_assigned:
            new_lit_assigned = False
            for clause in self.formula:
                clause_values = [self.compute_val(lit) for lit in clause]
                if 1 in clause_values:
                    continue
                if -1 not in clause_values:
                    logging.debug("Conflict detected in clause {}".format(clause))
                    conflict_lit = self.assign_conflict_lit(clause)
                    self.update_implication_graph(conflict_lit, [-lit for lit in clause if lit != conflict_lit])
                    return True, conflict_lit
                if sum(clause_values) == -1:
                    unassigned_lit = clause[clause_values.index(-1)]
                    self.assign_lit_from_clause(unassigned_lit, clause, level)
                    self.update_implication_graph(unassigned_lit, [-lit for lit in clause if lit != unassigned_lit])
                    new_lit_assigned = True
                    break
        return False, 0
    def assign_lit_from_clause(self, unassigned_lit, clause, level):
        assigned_value = 1 if unassigned_lit > 0 else 0
        ap = abs(unassigned_lit)
        logging.debug("Assigning value {} to {} from {}".format(assigned_value, ap, clause))
        self.assign_ap(ap, level, assigned_value)
    def get_learnt_clause(self, analysing_clause):
        learnt_clause = []
        for lit in analysing_clause:
            learnt_clause.append(-lit)
        return learnt_clause
    def conflict_analyse(self, conflict_lit, level):
        analysing_clause = [conflict_lit, -conflict_lit]
        levels = [self.assignments[abs(lit)][1] for lit in analysing_clause]
        while levels.count(level) != 1:
            logging.debug("Analysing {}".format(analysing_clause))
            next_lit = analysing_clause[0]
            parents = self.implication_graph[next_lit] if next_lit in self.implication_graph else [next_lit]
            analysing_clause = analysing_clause[1:] + [p for p in parents if p not in analysing_clause[1:]]
            levels = [self.assignments[abs(lit)][1] for lit in analysing_clause]
        backtrack_level = 0 if len(levels) < 2 else sorted(levels)[-2]
        learnt_clause = self.get_learnt_clause(analysing_clause)
        logging.debug("Learning new clause {}, levels {}".format(learnt_clause, levels))
        logging.debug("Backtrack to level {}".format(backtrack_level))
        return learnt_clause, backtrack_level
    def backtrack(self, backtrack_level, current_level):
        for level in range(backtrack_level, current_level+1):
            logging.debug("Clearing level {}".format(level))
            assigned_aps = self.level_assignments[level]
            for ap in assigned_aps:
                del self.assignments[ap]
                if ap in self.implication_graph:
                    del self.implication_graph[ap]
                if -ap in self.implication_graph:
                    del self.implication_graph[-ap]
            del self.level_assignments[level]
            del self.level_forced_assign_ap_map[level]
    def solve(self):
        self.assign_pure_aps()
        level = 0
        while True:
            if level == 0:
                unit_assignable = self.assign_unit_clause()
                if not unit_assignable:
                    return False
                conflict, conflict_lit = self.propagate_assignments(level)
                if conflict:
                    return False
                level += 1
            else:
                all_assigned = self.force_assign_ap(level)
                if all_assigned:
                    return True
                conflict, conflict_lit = self.propagate_assignments(level)
                if conflict:
                    learnt_clause, backtrack_level = self.conflict_analyse(conflict_lit, level)
                    self.formula = [learnt_clause] + self.formula
                    if backtrack_level != 0:
                        self.backtrack(backtrack_level, level)
                    level = backtrack_level
                else:
                    level += 1