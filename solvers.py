import datetime
import time
import random

class BaselineDPLLSolver(object):
    def get_ap_counts(self, formula):
        ap_counts = {}
        for clause in formula:
            for ap in clause:
                ap_counts[ap] = 0 if ap not in ap_counts else ap_counts[ap]
                ap_counts[ap] += 1
        return ap_counts
    
    def assign_ap(self, formula):
        ap_counts = self.get_ap_counts(formula)
        return random.choice(ap_counts.keys())

    def resolve_by_ap(self, formula, ap):
        resolved_formula = []
        for clause in formula:
            if -ap in clause:
                resolved_clause = [literal for literal in clause if literal != -ap]
                if len(resolved_clause) == 0:
                    return {
                        "formula": [[]],
                        "stop_early": True,
                        "unsat": True
                    }
                resolved_formula.append(resolved_clause)
            elif ap not in clause:
                resolved_formula.append(clause)
        return {
            "formula": resolved_formula
        }

    def resolve_by_pure_aps(self, formula):
        ap_counts = self.get_ap_counts(formula)
        assignments = []
        pure_aps = []
        for ap, counts in ap_counts.items():
            if -ap not in ap_counts:
                pure_aps.append(ap)
        for pure_ap in pure_aps:
            formula = self.resolve_by_ap(formula, pure_ap)["formula"]
        assignments += pure_aps
        return {
            "formula": formula,
            "assignments": assignments
        }

    def unit_propagation(self, formula):
        assignments = []
        single_ap_clauses = [clause for clause in formula if len(clause) == 1]
        while len(single_ap_clauses) > 0:
            res_resolve_by_ap = self.resolve_by_ap(formula, single_ap_clauses[0][0])
            formula = res_resolve_by_ap["formula"]
            if "unsat" in res_resolve_by_ap and res_resolve_by_ap["unsat"]:
                return {
                    "formula": formula,
                    "unsat": True,
                    "assignments": []
                }
            if not formula:
                return {
                    "formula": formula,
                    "assignments": assignments
                }
            assignments += single_ap_clauses[0]
            single_ap_clauses = [clause for clause in formula if len(clause) == 1]
        return {
            "formula": formula,
            "assignments": assignments
        }
    
    def _solve(self, formula, assignments=[]):
        print("Solving with formula", formula, "assignments", assignments)
        res_resolve_by_pure_aps = self.resolve_by_pure_aps(formula)
        print("Res by pure aps", res_resolve_by_pure_aps)
        formula, assignments_from_pure_aps = res_resolve_by_pure_aps["formula"], res_resolve_by_pure_aps["assignments"]
        res_unit_propagation = self.unit_propagation(formula)
        print("Res by unit propa", res_unit_propagation)
        formula, assignments_from_unit_propagation = res_unit_propagation["formula"], res_unit_propagation["assignments"]
        assignments += assignments_from_pure_aps + assignments_from_unit_propagation
        if "unsat" in res_unit_propagation and res_unit_propagation["unsat"]:
            return {
                "formula": formula,
                "assignments": [],
                "unsat": True
            }
        if not formula:
            return {
                "formula": formula,
                "assignments": assignments
            }
        
        next_ap = self.assign_ap(formula)
        print("Next ap", next_ap)
        res_solve = self._solve(self.resolve_by_ap(formula, next_ap)["formula"], assignments + [next_ap])
        if "unsat" in res_solve and res_solve["unsat"]:
            res_solve = self._solve(self.resolve_by_ap(formula, -next_ap)["formula"], assignments + [-next_ap])
        return res_solve

    def solve(self, cnf):
        formula = cnf.formula
        assignments = []
        start_time = time.clock()
        solution = self._solve(formula, assignments)
        elapse = time.clock() - start_time
        return {
            "time": str(datetime.timedelta(seconds=elapse)),
            "solution": solution
        }
        