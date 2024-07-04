# SAT Solver for imbalanced instances - Lukas Kaas Andersen

import sys
import time
import random
import threading

class DPLL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = {}
        self.assignment = {}
        self.literals_polarities = {}
        self.pure_literals = []

    def add_clause(self, clause):
        self.clauses[tuple(clause)] = "Unresolved"
        for literal in clause:
            if abs(literal) in self.literals.keys():
                self.literals[abs(literal)] += 1
                self.literals_polarities[literal] += 1
            else:
                self.literals_polarities[literal] = 1
                if literal < 0:
                    self.literals_polarities[abs(literal)] = 0
                else:
                    self.literals_polarities[0 - literal] = 0
                self.literals[abs(literal)] = 1

    def get_clauses(self):
        return self.clauses
        
    def get_literals(self):
        return self.literals
        
    def get_assignment(self):
        return self.assignment
    
    def get_literals_polarities(self):
        return self.literals_polarities
        
    def dpll(self):
        if self.check_satisfiability():
            return True
        elif self.check_conflict():
            return False
        else: 
            if not bool(self.pure_literals) is not True:
                pure_literal = self.pure_literals.pop()
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
            
            literal = self.choose_literal([])
            
            if literal is None:
                return False
            if self.literals_polarities.get(literal) > self.literals_polarities.get(0 - int(literal)):
                assignment = True
            else:
                assignment  = False
            self.assignment[literal] = assignment
            
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]

            self.assignment[abs(literal)] = not assignment
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
            
    def choose_literal(self, literals):
        if literals == []:
            unassigned_literals = [l for l in self.literals if l not in self.assignment]
            max_literal = max(unassigned_literals, key=self.literals.get)
            max_value = self.literals.get(max_literal)
            max_variables = [l for l in unassigned_literals if self.literals.get(l) == max_value]
            return random.choice(max_variables)
        elif literals != []:
            max_literals = []
            max_occurrence = 0
            for l in literals:
                occurrence = self.literals.get(abs(l))
                if occurrence > max_occurrence:
                    max_literals = []
                    max_literals.append(l)
                    max_occurrence = occurrence
                elif occurrence == max_occurrence:
                    max_literals.append(l)
            return random.choice(max_literals)
        else:
            return None
        
    def find_unit_clause_literal(self):
        unit_literals = []
        one_off_unit_literals = []
        for c in self.clauses:
            if self.clauses[c] == "Unit":
                for literal in c:
                    if abs(literal) not in self.assignment:
                        if abs(literal) not in unit_literals:
                            unit_literals.append(literal)
            elif self.clauses[c] == "One Off Unit":
                for literal in c:
                    if abs(literal) not in self.assignment:
                        if abs(literal) not in one_off_unit_literals:
                            one_off_unit_literals.append(literal)
        if unit_literals != []:
            return random.choice(unit_literals)
        elif one_off_unit_literals != []:
            return self.choose_literal(one_off_unit_literals)
        else:
            return False
        
    def populate_pure_literal(self):
        for literal in self.literals:
            positive_literal = self.literals_polarities.get(literal)
            negative_literal = self.literals_polarities.get(0 - literal)
            if (positive_literal == 0 and negative_literal != 0):
                self.pure_literals.append(0 - literal)
            elif (positive_literal != 0 and negative_literal == 0):
                self.pure_literals.append(literal)
        for c in self.clauses:
            if len(c) == 1:
                self.pure_literals.append(c[0])
            
    def check_satisfiability(self):
        r = True
        for clause in self.clauses:
            clause_satisfied = False
            for literal in clause:
                if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                    clause_satisfied = True
                    if self.clauses[clause] != "Resolved":
                        for l in clause:
                            self.literals[abs(l)] -= 1
                        self.clauses[clause] = "Resolved"
                    break
            if not clause_satisfied:
                if self.check_unit_clause(clause):
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "Unit"
                elif self.check_close_unit_clause(clause):
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "One Off Unit"
                else:
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                        self.clauses[clause] = "Unresolved"
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
                
    def check_close_unit_clause(self, clause):
        assigned_variables = 0
        for literal in clause:
            if abs(literal) in self.assignment:
                assigned_variables += 1
        if assigned_variables == len(clause) - 2:
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
    print(solver.get_literals_polarities())
    solver.populate_pure_literal()
    
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
    end_time = time.time()
    print("Time taken to solve: ", end_time - start_time, "seconds")
    print("Assignment: ", solver.get_assignment())