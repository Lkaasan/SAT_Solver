# SAT Solver for imbalanced instances - Lukas Kaas Andersen

import sys
import time

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
        print("Assignment: " , self.assignment)
        
    def returnClauseStatus(self):
        print(self.clause_status)
        
    def dpll(self):
        if self.check_satisfiability():
            return True
        else:
            pure_literal = self.find_pure_literal()
            unit_clause_literal = self.find_unit_clause_literal()
            if pure_literal is not False:
                if pure_literal < 0:
                    self.assignment[abs(pure_literal)] = False
                else:
                    self.assignment[pure_literal] = True
                if self.dpll():
                    return True
                else:
                    del self.assignment[abs(pure_literal)]       
            # elif unit_clause_literal is not False:
            #     if unit_clause_literal < 0:
            #         self.assignment[abs(unit_clause_literal)] = False
            #     else:
            #         self.assignment[unit_clause_literal] = True
            #     if self.dpll():
            #         return True
            #     else:
            #         del self.assignment[abs(unit_clause_literal)]

            literal = self.choose_literal()
            if literal is None:
                return False

            self.assignment[abs(literal)] = True
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]

            self.assignment[abs(literal)] = False
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]
        return False
    
    def choose_literal(self):
        unassigned_literals = [l for l in self.literals if l not in self.assignment]
        if unassigned_literals:
            return max(unassigned_literals, key=self.literals.get)
        else:
            return None
        
    def find_unit_clause_literal(self):
        for index, c in enumerate(self.clauses):
            if self.clause_status[index] == "Unit":
                for literal in c:
                    if abs(literal) not in self.assignment:
                        return literal
        return False
                
        
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
                if self.check_unit_clause(clause):
                    self.clause_status[index] = "Unit"
                else:
                    self.clause_status[index] = "Unresolved"
                r = False
        if r:
            return True
        else: 
            return False
        
    def check_unit_clause(self, clause):
        assigned_variables = 0
        for literal in clause:
            if abs(literal) in self.assignment:
                assigned_variables += 1
        if assigned_variables == 1:
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
    start_time = time.time()
    if len(sys.argv) != 2:
        print("Usage: py temp.py <filename>")
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
    end_time = time.time()
    print("Time taken to solve: ", end_time - start_time, "seconds")
    solver.returnAssignment()
    solver.returnClauseStatus()
