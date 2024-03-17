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
        if self.check_satisfiability():
            print(self.assignment)
            return True
        else:
            l = self.find_pure_literal()
            if l is not False:
                if l < 0:
                    self.assignment[abs(l)] = False
                else: 
                    self.assignment[1] = True
                self.dpll()

            # If there's no pure literal, choose a literal to branch on
            literal = self.choose_literal()
            if literal is None:
                return False

            # Try assigning true
            self.assignment[abs(literal)] = True
            if self.dpll():
                return True
            else:
                # Backtrack
                del self.assignment[abs(literal)]

            # Try assigning false
            self.assignment[abs(literal)] = False
            if self.dpll():
                return True
            else:
                # Backtrack
                del self.assignment[abs(literal)]
        return False

    def choose_literal(self):
        # Choose a literal with the minimum occurrences
        unassigned_literals = [l for l in self.literals if l not in self.assignment]
        if unassigned_literals:
            return max(unassigned_literals, key=self.literals.get)
        else:
            return None
        
    def find_pure_literal(self):
        for c in self.clauses:
            if len(c) == 1 and abs(c[0]) not in self.assignment:
                return c[0]
        return False
 
    def check_satisfiability(self):
        for clause in self.clauses:
            clause_satisfied = False
            for literal in clause:
                if (literal > 0 and self.assignment.get(literal) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
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
    solver.returnLiterals()
    solver.returnClauses()
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
