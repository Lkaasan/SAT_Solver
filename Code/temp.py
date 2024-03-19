import sys

class DPLL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = []
        self.clause_status = []
        self.assignment = {}

    def addClause(self, clause):
        self.clauses.append(clause)
        self.clause_status.append("Unresolved")
        for literal in clause:
            if abs(literal) in self.literals.keys():
                self.literals[abs(literal)] += 1
            else:
                self.literals[abs(literal)] = 1

    def returnClauses(self):
        print(self.clauses)
        
    def returnLiterals(self):
        print(self.literals)
        
    def returnAssignment(self):
        print(self.assignment)
        
    def dpll(self):
        print(self.clauses)
        print(self.clause_status)
        print(self.assignment)
        if self.check_satisfiability():
            return True
        else:
            l = self.find_pure_literal()
            if l is not False:
                if l < 0:
                    self.assignment[abs(l)] = False
                else:
                    self.assignment[l] = True
                if self.dpll():
                    return True
                else:
                    del self.assignment[abs(l)]

            literal = self.choose_literal()
            if literal is None:
                return False

            # Try assigning true
            self.assignment[abs(literal)] = True
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]

            # Try assigning false
            self.assignment[abs(literal)] = False
            if self.dpll():
                return True
            else:
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
        r = True
        for index, clause in enumerate(self.clauses):
            clause_satisfied = False
            for literal in clause:
                if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                    clause_satisfied = True
                    self.clause_status[index] = "Resolved"
                    break
            if not clause_satisfied:
                r = False
                self.clause_status[index] = "Unresolved"
        if r:
            return True
        else: 
            return False
            

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
    solver.returnAssignment()
