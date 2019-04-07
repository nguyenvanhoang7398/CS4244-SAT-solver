from pycryptosat import Solver
from base_solver import BaseSolver

class CryptoSat(BaseSolver):
    def solve_sat(self):
        solver = Solver()
        for clause in self.formula:
            solver.add_clause(clause)
        sat, assignments = solver.solve()
        return sat
