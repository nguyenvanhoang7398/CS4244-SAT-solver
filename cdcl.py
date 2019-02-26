import datetime
import time
import random
import pprint

class CDCL(object):
    def __init__(self, formula, literals):
        self.formula = formula
        self.literals = literals
        self.assignments = {}
        for lit in literals:
            self.assignments[lit] = -1
        self.implication_graph = {} # (parent, 1), (child, 0)
    def propagate_assignment(self):
        new_lit_assigned = True
        while new_lit_assigned:
            new_lit_assigned = False
            for clause in self.formula:
                clause_values = [self.compute_val(lit) for lit in clause]
                print(clause, clause_values)
                if 1 in clause_values:
                    continue
                if -1 not in clause_values:
                    return True
                if sum(clause_values) == -1:
                    print("assignable")
                    unassigned_lit = clause[clause_values.index(-1)]
                    conflict = self.assign_lit_from_clause(unassigned_lit, clause)
                    if conflict:
                        return True
                    new_lit_assigned = True
                    break
        return False
    def assign_lit_from_clause(self, unassigned_lit, clause):
        assigned_value = 1 if unassigned_lit > 0 else 0
        print("assigning value {} to {}".format(assigned_value, unassigned_lit))
        if self.assignments[unassigned_lit] != -1 and assigned_value != self.assignments[unassigned_lit]:
            return True
        self.assignments[unassigned_lit] = assigned_value
        if unassigned_lit not in self.implication_graph:
                self.implication_graph[unassigned_lit] = []
        for lit in clause:
            if lit != unassigned_lit:
                if -lit not in self.implication_graph:
                    self.implication_graph[-lit] = []
                self.implication_graph[-lit].append((unassigned_lit, 0))
                self.implication_graph[unassigned_lit].append((-lit, 1))
        return False
    def compute_val(self, lit):
        if self.assignments[abs(lit)] == -1:
            return -1
        elif self.assignments[abs(lit)] == 1:
            return 1 if lit > 0 else 0
        return 1 if lit < 0 else 0
    def solve(self):
        self.assignments[1] = 1
        conflict = self.propagate_assignment()
        print(self.assignments, conflict)
        self.assignments[2] = 1
        conflict = self.propagate_assignment()
        print(self.assignments, conflict)
        self.assignments[4] = 1
        conflict = self.propagate_assignment()
        print(self.assignments, conflict)
        pprint.pprint(self.implication_graph)