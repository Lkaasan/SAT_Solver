import sys

class Literal:
    def __init__(self, name, negated=False):
        self.name = name
        self.negated = negated

    def get_name(self):
        return self.name

    def is_negated(self):
        return self.negated


class Clause:
    def __init__(self, literals):
        self.literals = literals
        self.status = "Unresolved"

    def get_literals(self):
        return self.literals

    def get_status(self):
        return self.status

    def set_status(self, s):
        self.status = s


class Solver:
    
    def __init__(self):
        self.temp = 0


def read_dimacs_file(filename):
    cnf_formula = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('c') or line.startswith('p'):
                continue  # Skip comment lines and problem description lines
            clause = [int(x) for x in line.strip().split() if x != '0']
            if clause:
                cnf_formula.append(clause)
    return cnf_formula


if __name__ == "__main__":
   file = sys.argv[1]
   cnf = read_dimacs_file(file)
   for clause in cnf:
       clause = []