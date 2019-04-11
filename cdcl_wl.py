from cdcl import CDCL
import logging

class CDCL_WL(CDCL):
    def __init__(self, formula, atomic_props, log_level=None, log_file=None, branching_heuristic=None, model_path=None):
        super(CDCL_WL, self).__init__(formula, atomic_props, log_level, log_file, branching_heuristic, model_path)
        self.init_hash_refs_map()
    def init_hash_refs_map(self):
        # self.wl_refs = {}
        self.hash_refs_map = {}
        for clause_hash, clause in self.hash_clause_map.items():
            self.hash_refs_map[clause_hash] = [0, len(clause)-1]
        # for clause in self.formula:
        #     for lit in clause:
        #         if abs(lit) not in self.wl_refs:
        #             self.wl_refs[abs(lit)] = []
        #         self.wl_refs[abs(lit)].append([0, len(clause)-1])
    def update_learnt_clause(self, learnt_clause):
        clause_hash = self.hash_clause(learnt_clause)
        self.hash_clause_map[clause_hash] = learnt_clause
        self.formula.append(learnt_clause)
        for lit in learnt_clause:
            # self.var_clause_map[abs(lit)].append(learnt_clause)
            self.var_hash_map[abs(lit)].append(clause_hash)
        self.hash_refs_map[clause_hash] = [0, len(learnt_clause)-1]
    def check_clause_status(self, var, i):
        clause_hash = self.var_hash_map[var][i]
        refs = self.hash_refs_map[clause_hash]
        clause = self.get_involved_clauses(var)[i]
        return self._check_clause_status(refs, refs[0], refs[1], clause)
    def _check_clause_status(self, refs, start_ref0, start_ref1, clause):
        val_ref0 = self.compute_val(clause[refs[0]], self.assignments)
        val_ref1 = self.compute_val(clause[refs[1]], self.assignments)
        clause_size = len(clause)
        if val_ref0 == 1 or val_ref1 == 1:
            return "sat-unassaigned", [], 0
        if val_ref0 == -1 and val_ref1 == -1:
            if refs[0] != refs[1]:
                return "sat-unassaigned", [], 0
            if (refs[0] + 1) % clause_size == start_ref0:
                return "unit", clause, clause[refs[0]]
            refs[0] = (refs[0] + 1) % clause_size
            return self._check_clause_status(refs, start_ref0, start_ref1, clause)
        if val_ref0 == 0 and val_ref1 == -1:
            if (refs[0] + 1) % clause_size == start_ref0:
                return "unit", clause, clause[refs[1]]
            refs[0] = (refs[0] + 1) % clause_size
            return self._check_clause_status(refs, start_ref0, start_ref1, clause)
        if val_ref0 == -1 and val_ref1 == 0:
            if (refs[1] + 1) % clause_size == start_ref1:
                return "unit", clause, clause[refs[0]]
            refs[1] = (refs[1] + 1) % clause_size
            return self._check_clause_status(refs, start_ref0, start_ref1, clause)
        if val_ref0 == 0 and val_ref1 == 0:
            if (refs[0] + 1) % clause_size == start_ref0:
                logging.debug("Conflict detected in clause {}".format(clause))
                return "conflict", clause, 0
            refs[0] = (refs[0] + 1) % clause_size
            return self._check_clause_status(refs, start_ref0, start_ref1, clause)
        raise Exception("Unaccounted clause staus: val_ref0 {}, val_ref1 {}, refs {}, clause {}".format(val_ref0, val_ref1, refs, clause))