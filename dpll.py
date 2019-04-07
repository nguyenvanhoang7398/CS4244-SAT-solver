import datetime
import time
import random
import logging
from base_solver import BaseSolver
import copy

class DPLL(BaseSolver):
    def get_lit_counts(self, formula):
        ap_counts = {}
        for clause in formula:
            for ap in clause:
                ap_counts[ap] = 0 if ap not in ap_counts else ap_counts[ap]
                ap_counts[ap] += 1
        return ap_counts
    def get_pure_lits(self, formula):
        lit_counts = self.get_lit_counts(formula)
        pure_lits = [lit for lit, _ in lit_counts.items() if -lit not in lit_counts]
        logging.debug("Pure aps in formula {}: {}".format(formula, pure_lits))
        return pure_lits
    def resolve_by_pure_aps(self, formula):
        pure_aps = self.get_pure_lits(formula)
        for pure_ap in pure_aps:
            formula, _, unsat = self.resolve_by_lit(formula, pure_ap)
            if unsat:
                raise Exception("Resolving pure ap should not return UNSAT")
        return formula, pure_aps, False
    def resolve_by_unit_propagation(self, formula):
        assignments = []
        single_ap_clauses = self.get_unit_lits(formula)
        while len(single_ap_clauses) > 0:
            ap = single_ap_clauses[0]
            formula, _, unsat = self.resolve_by_lit(formula, ap)
            if unsat:
                return formula, [], True
            if not formula:
                return formula, assignments, False
            assignments.append(ap)
            single_ap_clauses = self.get_unit_lits(formula)
        return formula, assignments, False
    def debug_msg(self, level, task, formula, assignments, unsat):
        logging.debug("Level {}, resolution by {}:".format(level, task))
        logging.debug("- Formula: {}".format(formula))
        logging.debug("- Assignments: {}".format(assignments))
        logging.debug("- Unsat: {}".format(unsat))
    def add_to_assignments(self, assignments, lits):
        copied_assignments = copy.deepcopy(assignments)
        for lit in lits:
            copied_assignments[lit] = 1 if lit > 0 else 0
        return copied_assignments
    def _solve(self, level, formula, assignments={}):
        formula, pure_aps, unsat = self.resolve_by_pure_aps(formula)
        if unsat:
            raise Exception("Resolving pure aps should not return UNSAT")
        assignments = self.add_to_assignments(assignments, pure_aps)
        self.debug_msg(level, "pure aps", formula, assignments, unsat)
        formula, new_assignments, unsat = self.resolve_by_unit_propagation(formula)
        assignments = self.add_to_assignments(assignments, new_assignments)
        self.debug_msg(level, "unit propagation", formula, assignments, unsat)
        if unsat:
            return formula, assignments, True
        if not formula:
            return formula, assignments, False
        next_ap = self.assign_next_var(formula, assignments)
        logging.debug("Assigning next ap: {}".format(next_ap))
        tmp_formula, tmp_assignments, unsat = self.resolve_by_lit(formula, next_ap)
        self.debug_msg(level, "assigning {}".format(next_ap), tmp_formula, self.add_to_assignments(assignments, tmp_assignments), unsat)
        if unsat:
            raise Exception("Resolving an ap after all unit clauses have been resolved should not return UNSAT")
        tmp_formula, tmp_assignments, unsat = self._solve(level+1, tmp_formula, self.add_to_assignments(assignments, [next_ap]))
        self.debug_msg(level, "solving", tmp_formula, tmp_assignments, unsat)
        if unsat:
            logging.debug("Assigning {} as next ap returns UNSAT, start backtracking".format(next_ap))
            tmp_formula, tmp_assignments, unsat = self.resolve_by_lit(formula, -next_ap)
            self.debug_msg(level, "assigning {}".format(next_ap), tmp_formula, self.add_to_assignments(assignments, tmp_assignments), unsat)
            if unsat:
                raise Exception("Resolving an ap after all unit clauses have been resolved should not return UNSAT")
            tmp_formula, tmp_assignments, unsat = self._solve(level+1, tmp_formula, self.add_to_assignments(assignments, [-next_ap]))
            self.debug_msg(level, "solving an ap", tmp_formula, tmp_assignments, unsat)
        return tmp_formula, tmp_assignments, unsat
    def solve_sat(self):
        assignments = {}
        _, assignments, unsat = self._solve(0, self.formula, assignments)
        sat = not unsat
        if sat:
            logging.debug("SAT")
        else:
            logging.debug("UNSAT")
        return sat