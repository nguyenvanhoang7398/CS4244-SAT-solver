from cdcl import CDCL
import logging
import copy
import numpy as np

class CDCL_WL(CDCL):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None, model_path=None):
        super(CDCL_WL, self).__init__(formula, atomic_props, log_level, log_file, branching_heuristic, model_path)
        self.init_hash_refs_map()
    def init_hash_refs_map(self):
        self.hash_refs_map = {}
        for clause_hash, clause in self.hash_clause_map.items():
            self.hash_refs_map[clause_hash] = [0, len(clause)-1]
    def shorten_formula(self, formula, assignment):
        shortened_formula = []
        for i, clause in enumerate(formula):
            shortened_clause = []
            if self.check_clause_status_wrapper(self.clause_idx_hash_map[i])[0] == "sat":
                continue
            for lit in clause:
                if self.compute_val(lit, assignment) == -1:
                    shortened_clause.append(lit)
            shortened_formula.append(shortened_clause)
        return shortened_formula
    def assign_var(self, var, level, value):
        assignable = super(CDCL_WL, self).assign_var(var, level, value)
        if assignable:
            true_lit = var if self.assignments[var][0] > 0 else -var
            for clause_idx, clause_hash in enumerate(self.lit_hash_map[true_lit]):
                if self.check_clause_status_wrapper(clause_hash)[0] != "sat":
                    clause = self.hash_clause_map[clause_hash]
                    self.hash_refs_map[clause_hash][0] = clause.index(true_lit)
        return assignable
    def update_learnt_clause(self, learnt_clause):
        clause_hash = super(CDCL_WL, self).update_learnt_clause(learnt_clause)
        self.hash_refs_map[clause_hash] = [0, len(learnt_clause)-1]
        return clause_hash
    def check_clause_status(self, clause_hash):
        refs = self.hash_refs_map[clause_hash]
        clause = self.hash_clause_map[clause_hash]
        ref_vals = [self.compute_val(clause[refs[0]], self.assignments), self.compute_val(clause[refs[1]], self.assignments)]
        if ref_vals[0] == 1 or ref_vals[1] == 1:
            return "sat", [], 0
        for i, ref in enumerate(refs):
            if ref_vals[i] == 0:
                for new_idx, lit in enumerate(clause):
                    lit_val = self.compute_val(lit, self.assignments)
                    if lit_val != 0 and new_idx not in refs:
                        refs[i] = new_idx
                        if lit_val == 1:
                            return "sat", [], 0
        ref_vals = [self.compute_val(clause[refs[0]], self.assignments), self.compute_val(clause[refs[1]], self.assignments)]
        num_false_lits = ref_vals.count(0)
        if num_false_lits == 0:
            return "sat-unassigned", [], 0
        elif num_false_lits == 1:
            unit_lit = clause[refs[1-ref_vals.index(0)]]
            return "unit", clause, unit_lit
        elif num_false_lits == 2:
            return "conflict", clause, 0
        raise Exception("Unaccounted clause staus: val_ref0 {}, val_ref1 {}, refs {}, clause {}".format(ref_vals[0], ref_vals[1], refs, clause))