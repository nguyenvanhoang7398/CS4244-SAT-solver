class CNF(object):
    def __init__(self, num_props=0, num_clauses=0, formula=[]):
        self.formula = formula
        self.num_props = num_props
        self.num_clauses = num_clauses
    def __str__(self):
        return str({
            "num_props": self.num_props,
            "num_clauses": self.num_clauses,
            "formula": self.formula
        })