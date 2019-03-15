import datetime
import time
import random
import pprint
from collections import deque
import logging

class DPLL(object):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None):
        self.formula = formula
        self.atomic_props = atomic_props
        self.assignments, self.level_assignments = {}, {}
        self.level_forced_assign_ap_map = {}
        self.set_log_level(log_level, log_file)
        self.backtracked = []
        self.visited = []
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
        logging.debug("Force assign {} as {} at level {}".format(ap, value, level))
        self.assign_ap(ap, level, value)
        self.level_forced_assign_ap_map[level] = ap
    def force_assign_ap(self, level):
        next_ap = self.ordered_assign_ap()
        if next_ap == 0:
            return True
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
                    return True
                if sum(clause_values) == -1:
                    unassigned_lit = clause[clause_values.index(-1)]
                    self.assign_lit_from_clause(unassigned_lit, clause, level)
                    new_lit_assigned = True
                    break
        return False
    def assign_lit_from_clause(self, unassigned_lit, clause, level):
        assigned_value = 1 if unassigned_lit > 0 else 0
        ap = abs(unassigned_lit)
        logging.debug("Assigning value {} to {} from {}".format(assigned_value, ap, clause))
        self.assign_ap(ap, level, assigned_value)
    def backtrack(self, backtrack_level, current_level):
        logging.debug("Backtracking to level {} from level {}".format(backtrack_level, current_level))
        for level in range(backtrack_level, current_level+1):
            logging.debug("Clearing level {}".format(level))
            assigned_aps = self.level_assignments[level]
            for ap in assigned_aps:
                del self.assignments[ap]
            if level > backtrack_level:
                self.visited.remove(level)
                self.backtracked.remove(level)
            del self.level_assignments[level]
            del self.level_forced_assign_ap_map[level]
    def solve(self):
        self.assign_pure_aps()
        level = 0
        all_assigned = False
        sat = True
        while not all_assigned:
            if level == 0:
                unit_assignable = self.assign_unit_clause()
                if not unit_assignable:
                    sat = False
                conflict = self.propagate_assignments(level)                                
                if conflict:
                    sat = False
                level += 1
                all_assigned = self.force_assign_ap(level)
            else:
                if level not in self.visited:
                    self.visited.append(level)
                else:
                    self.backtracked.append(level)
                conflict = self.propagate_assignments(level)
                if conflict:
                    backtrackable = False
                    for backtrack_level in reversed(self.visited):
                        if backtrack_level not in self.backtracked:
                            forced_assign_ap = self.level_forced_assign_ap_map[level]
                            forced_assign_ap_value = self.assignments[forced_assign_ap][0]
                            self.backtrack(backtrack_level, level)
                            level = backtrack_level
                            self._force_assign_ap(forced_assign_ap, level, 1-forced_assign_ap_value)
                            backtrackable = True
                            break
                    if not backtrackable:
                        sat = False
                        break
                else:
                    level += 1
                    all_assigned = self.force_assign_ap(level)
        if sat:
            logging.debug("SAT")
        else:
            logging.debug("UNSAT")
        return sat