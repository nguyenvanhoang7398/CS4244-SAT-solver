from pycryptosat import Solver

class CryptoSat(object):
    def __init__(self, formula, atomic_props):
        self.formula = formula
        self.atomic_props = atomic_props
        self.solver = Solver()
    def solve(self):
        for clause in self.formula:
            s.add_clause(clause)
        sat, assignments = s.solve()
        return sat
