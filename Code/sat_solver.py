# SAT Solver for imbalanced instances - Lukas Kaas Andersen

import sys
import time
import random

class DPLL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = []
        self.clause_status = []
        self.assignment = {}
        self.initial_pure_literal_count = 0
        self.pure_literal_tracker = 0

    def add_clause(self, clause):
        if len(clause) == 1:
            self.initial_pure_literal_count += 1
        self.clauses.append(clause)
        self.clause_status.append("Unresolved")
        for literal in clause:
            if abs(literal) in self.literals.keys():
                self.literals[abs(literal)] += 1
            else:
                self.literals[abs(literal)] = 1

    def get_clauses(self):
        return self.clauses
        
    def get_literals(self):
        return self.literals
        
    def get_assignment(self):
        return self.assignment
        
    def get_clause_status(self):
        return self.clause_status
        
    def dpll(self):
        print(self.assignment)
        if self.check_satisfiability():
            return True
        elif self.check_conflict():
            return False
        else:
            if self.pure_literal_tracker != self.initial_pure_literal_count:
                pure_literal = self.find_pure_literal()
                if pure_literal is not False:
                    self.pure_literal_tracker += 1
                    if pure_literal < 0:
                        self.assignment[abs(pure_literal)] = False
                    else:
                        self.assignment[pure_literal] = True
                    if self.dpll():
                        return True
                    else:
                        del self.assignment[abs(pure_literal)]     
            unit_clause_literal = self.find_unit_clause_literal()  
            if unit_clause_literal is not False:
                if unit_clause_literal < 0:
                    self.assignment[abs(unit_clause_literal)] = False
                else:
                    self.assignment[unit_clause_literal] = True
                if self.dpll():
                    return True
                else:
                    del self.assignment[abs(unit_clause_literal)]
            
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
    
    def check_conflict(self):
        for clause in self.clauses:
            assigned_literal = 0 
            all_false_checker = True
            for index, literal in enumerate(clause):
                if abs(literal) in self.assignment:
                    assigned_literal += 1
                    if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                        all_false_checker = False
            if assigned_literal == len(clause) and all_false_checker == True:
                return True
        return False
            

    def choose_literal(self):
        unassigned_literals = [l for l in self.literals if l not in self.assignment]
        if unassigned_literals:
            max_literal = max(unassigned_literals, key=self.literals.get)
            max_value = self.literals.get(max_literal)
            max_variables = [l for l in unassigned_literals if self.literals.get(l) == max_value]
            return random.choice(max_variables)
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
                    if self.clause_status[index] != "Resolved":
                        for l in clause:
                            self.literals[abs(l)] -= 1
                        self.clause_status[index] = "Resolved"
                    break
            if not clause_satisfied:
                if self.check_unit_clause(clause):
                    if self.clause_status[index] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                        self.clause_status[index] = "Unit"
                else:
                    if self.clause_status[index] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
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
        if assigned_variables == len(clause) - 1:
            return True
        else:
            return False

def read_dimacs_file(filename):
    cnf_formula = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('c') or line.startswith('p') or line.startswith('%') or line.startswith('0'):
                continue  
            clause = [int(x) for x in line.strip().split() if x != '0']
            if clause:
                cnf_formula.append(clause)
    return cnf_formula

if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) != 2:
        print("Usage: py sat_solver.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    cnf = read_dimacs_file(filename)
    solver = DPLL()
    for clause in cnf:
        solver.add_clause(clause)
    print(solver.get_literals())
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
    end_time = time.time()
    print("Time taken to solve: ", end_time - start_time, "seconds")
    print("Assignment: ", solver.get_assignment())
