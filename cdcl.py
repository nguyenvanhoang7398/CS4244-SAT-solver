import datetime
import time
import random
import pprint
from collections import deque, Counter
import logging
import operator

class CDCL(object):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None):
        self.formula = formula
        self.atomic_props = atomic_props
        self.assignments, self.level_assignments = {}, {}
        self.implication_graph, self.level_forced_assign_var_map = {}, {}
        self.set_log_level(log_level, log_file)
        self.assign_next_var = self.choose_branching_heuristic(branching_heuristic)
    def choose_branching_heuristic(self, branching_heuristic):
        if branching_heuristic == "random":
            return self.heuristic_random_assign_var
        if branching_heuristic == "2clause":
            return self.heuristic_2clause_assign_var
        return self.heuristic_ordered_assign_var
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
    def heuristic_ordered_assign_var(self):
        for var in self.atomic_props:
            if var not in self.assignments:
                return var
        return 0
    def _force_assign_var(self, var, level, value):
        self.assign_var(var, level, value)
        self.level_forced_assign_var_map[level] = var
    def heuristic_2clause_assign_var(self):
        unassigned_var_counts = {}
        for clause in self.formula:
            unassigned_lits = [lit for lit in clause if abs(lit) not in self.assignments]
            if len(unassigned_lits) == 2:
                for lit in unassigned_lits:
                    if abs(lit) not in unassigned_var_counts:
                        unassigned_var_counts[abs(lit)] = 0
                    unassigned_var_counts[abs(lit)] += 1
        if len(unassigned_var_counts) == 0:
            return self.heuristic_ordered_assign_var()
        max_count = max(unassigned_var_counts.values())
        most_occuring_vars = [var for var in unassigned_var_counts.keys() if unassigned_var_counts[var] == max_count]
        return random.choice(most_occuring_vars)
    def heuristic_random_assign_var(self):
        unassigned_vars = [var for var in self.atomic_props if var not in self.assignments]
        return 0 if len(unassigned_vars) == 0 else random.choice(unassigned_vars)
    def force_assign_var(self, level):
        next_var = self.assign_next_var()
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
    def compute_val(self, lit):
        if abs(lit) not in self.assignments:
            return -1
        elif self.assignments[abs(lit)][0] == 1:
            return 1 if lit > 0 else 0
        return 1 if lit < 0 else 0
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
                clause_values = [self.compute_val(lit) for lit in clause]
                if 1 in clause_values:
                    continue
                if -1 not in clause_values:
                    logging.debug("Conflict detected in clause {}".format(clause))
                    conflict_lit = self.assign_conflict_lit(clause, level)
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
        var = abs(unassigned_lit)
        logging.debug("Assigning value {} to {} from {}".format(assigned_value, var, clause))
        self.assign_var(var, level, assigned_value)
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
                conflict, conflict_lit = self.deduce(level)
                if conflict:
                    sat = False
                    break
                level += 1
                all_assigned = self.force_assign_var(level)
            else:
                conflict, conflict_lit = self.deduce(level)
                if conflict:
                    if conflict_lit in self.implication_graph:
                        logging.debug("Before bt Conflict lits in implication graph {}".format(self.implication_graph[conflict_lit]))
                    if -conflict_lit in self.implication_graph:
                        logging.debug("Before bt Conflict lits in implication graph {}".format(self.implication_graph[-conflict_lit]))                                        
                    learnt_clause, backtrack_level = self.conflict_analyse(conflict_lit, level)
                    self.formula = [learnt_clause] + self.formula
                    forced_assign_var, forced_assign_var_value = self.backtrack(backtrack_level, level)
                    if conflict_lit in self.implication_graph:
                        logging.debug("After bt Conflict lits in implication graph {}".format(self.implication_graph[conflict_lit]))
                    if -conflict_lit in self.implication_graph:
                        logging.debug("After bt Conflict lits in implication graph {}".format(self.implication_graph[-conflict_lit]))                    
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