import sys

class DPLL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = []
        self.assignment = {}

    def addClause(self, clause):
        self.clauses.append(clause)
        for literal in clause:
            if abs(literal) in self.literals.keys():
                self.literals[abs(literal)] += 1
            else:
                self.literals[abs(literal)] = 1

    def returnClauses(self):
        print(self.clauses)
        
    def returnLiterals(self):
        print(self.literals)
        
    def dpll(self):
        assignment = self.assignment
        if assignment is not None:
            l = self.choose_literal()
        else:
            

    def choose_literal(self):
        # Choose a literal with the minimum occurrences
        unassigned_literals = [l for l in self.literals if l not in self.assignment]
        if unassigned_literals:
            return max(unassigned_literals, key=self.literals.get)
        else:
            return None
        
    def check_satisfiability(self):
        for clause in self.clauses:
            clause_satisfied = False
            for literal in clause:
                if (literal > 0 and self.assignment.get(literal)) or \
                   (literal < 0 and not self.assignment.get(abs(literal))):
                    clause_satisfied = True
                    break
            if not clause_satisfied:
                return False
        return True

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
    if len(sys.argv) != 2:
        print("Usage: python dpll.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    cnf = read_dimacs_file(filename)
    solver = DPLL()
    for clause in cnf:
        solver.addClause(clause)
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
