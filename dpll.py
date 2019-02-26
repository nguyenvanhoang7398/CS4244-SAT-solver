import datetime
import time
import random

class DPLL(object):
    def get_ap_counts(self, formula):
        ap_counts = {}
        for clause in formula:
            for ap in clause:
                ap_counts[ap] = 0 if ap not in ap_counts else ap_counts[ap]
                ap_counts[ap] += 1
        return ap_counts
    def get_pure_aps(self, formula):
        ap_counts = self.get_ap_counts(formula)
        pure_aps = [ap for ap, _ in ap_counts.items() if -ap not in ap_counts]
        print("Pure aps in formula {}: {}".format(formula, pure_aps))
        return pure_aps
    def assign_ap(self, formula):
        return self.uniform_assign_ap(formula)
    def uniform_assign_ap(self, formula):
        ap_counts = self.get_ap_counts(formula)
        return random.choice(ap_counts.keys())
    def resolve_by_ap(self, formula, ap):
        resolved_formula = []
        for clause in formula:
            if -ap in clause:
                resolved_clause = [literal for literal in clause if literal != -ap]
                if len(resolved_clause) == 0:
                    return resolved_formula, [ap], True
                resolved_formula.append(resolved_clause)
            elif ap not in clause:
                resolved_formula.append(clause)
        return resolved_formula, [ap], False
    def resolve_by_pure_aps(self, formula):
        pure_aps = self.get_pure_aps(formula)
        for pure_ap in pure_aps:
            formula, _, unsat = self.resolve_by_ap(formula, pure_ap)
            if unsat:
                raise Exception("Resolving pure ap should not return UNSAT")
        return formula, pure_aps, False
    def get_single_ap_clauses(self, formula):
        return [clause for clause in formula if len(clause) == 1]
    def resolve_by_unit_propagation(self, formula):
        assignments = []
        single_ap_clauses = self.get_single_ap_clauses(formula)
        while len(single_ap_clauses) > 0:
            ap = single_ap_clauses[0][0]
            formula, _, unsat = self.resolve_by_ap(formula, ap)
            if unsat:
                return formula, [], True
            if not formula:
                return formula, assignments, False
            assignments.append(ap)
            single_ap_clauses = self.get_single_ap_clauses(formula)
        return formula, assignments, False
    def debug_msg(self, level, task, formula, assignments, unsat):
        print("Level {}, resolution by {}:".format(level, task))
        print("- Formula: {}".format(formula))
        print("- Assignments: {}".format(assignments))
        print("- Unsat: {}".format(unsat))
    def _solve(self, level, formula, assignments=[]):
        formula, pure_aps, unsat = self.resolve_by_pure_aps(formula)
        if unsat:
            raise Exception("Resolving pure aps should not return UNSAT")
        assignments += pure_aps
        self.debug_msg(level, "pure aps", formula, assignments, unsat)
        formula, new_assignments, unsat = self.resolve_by_unit_propagation(formula)
        assignments += new_assignments
        self.debug_msg(level, "unit propagation", formula, assignments, unsat)
        if unsat:
            return formula, assignments, True
        if not formula:
            return formula, assignments, False
        next_ap = self.assign_ap(formula)
        print("Assigning next ap:", next_ap)
        tmp_formula, tmp_assignments, unsat = self.resolve_by_ap(formula, next_ap)
        self.debug_msg(level, "assigning {}".format(next_ap), tmp_formula, assignments + tmp_assignments, unsat)
        if unsat:
            raise Exception("Resolving an ap after all unit clauses have been resolved should not return UNSAT")
        tmp_formula, tmp_assignments, unsat = self._solve(level+1, tmp_formula, assignments + [next_ap])
        self.debug_msg(level, "solving", tmp_formula, tmp_assignments, unsat)
        if unsat:
            print("Assigning {} as next ap returns UNSAT, start backtracking".format(next_ap))
            tmp_formula, tmp_assignments, unsat = self.resolve_by_ap(formula, -next_ap)
            self.debug_msg(level, "assigning {}".format(next_ap), tmp_formula, assignments + tmp_assignments, unsat)
            if unsat:
                raise Exception("Resolving an ap after all unit clauses have been resolved should not return UNSAT")
            tmp_formula, tmp_assignments, unsat = self._solve(level+1, tmp_formula, assignments + [-next_ap])
            self.debug_msg(level, "solving an ap", tmp_formula, tmp_assignments, unsat)
        return tmp_formula, tmp_assignments, unsat
    def solve(self, cnf):
        formula = cnf.formula
        assignments = []
        start_time = time.clock()
        formula, assignments, unsat = self._solve(0, formula, assignments)
        elapse = time.clock() - start_time
        return assignments, unsat, elapse