import sys
import time
import random


class CDCL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = {}
        self.assignment = {}
        self.learned_clauses = []
        self.decision_stack = []
        self.decision_level = 0
    
    def add_clause(self, clause):
        if len(clause) == 1:
            self.clauses[tuple(clause)] = "Unit"
        else:
            self.clauses[tuple(clause)] = "Unresolved"
        for literal in clause:
            if abs(literal) in self.literals.keys():
                self.literals[abs(literal)] += 1
            else:
                self.literals[abs(literal)] = 0
    
    def get_clauses(self):
        return self.clauses
        
    def get_literals(self):
        return self.literals
    
    def get_unassigned_literals(self):
        return [literal for literal in self.literals if literal not in self.assignment]
    
    def dpll(self):
        while True:
            self.unit_propogation()
            self.change_clause_states()
            print(self.clauses)
            if (self.conflict_analysis):
                if (self.decision_level == 0):
                    return False
                self.backtack()
            elif not self.get_unassigned_literals():
                return True
            else:
                self.make_decision()
            
    def change_clause_states(self):
        for clause in self.clauses:
            clause_satisfied = False
            for literal in clause:
                if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                    clause_satisfied = True
                    if self.clauses[clause] != "Resolved":
                        self.clauses[clause] = "Resolved"
                    break
            if not clause_satisfied:
                if self.check_unit_clause(clause):
                    self.clauses[clause] == "Unit"
                elif self.check_conflict_clause(clause):
                    self.clauses[clause] == "Conflict"
                else:
                    self.clauses[clause] == "Unresolved"
                    
    def check_conflict_clause(self, clause):
        assigned_variables = 0
        for l in clause:
            if abs(l) in self.assignment:
                assigned_variables += 1
        if assigned_variables == len(clause):
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
    
    def unit_propogation(self):
        for clause in self.clauses:
            if self.clauses.get(clause) == "Unit":
                self.assign_unit_clause(clause)
    
    def assign_unit_clause(self, clause):
        for literal in clause:
            if literal not in self.assignment:
                if literal < 0:
                    self.assignment[literal] == False
                else:
                    self.assignment[literal] == True
                            
    def conflict_analysis(self):    
        conflicting_clauses = []
        for clause in self.clauses:
            if self.clauses.get(clause) == "Conflict":
                conflicting_clauses.append(clause)
        if conflicting_clauses == []:
            return False
        else:
            self.learn_clause()
            return True
    
    
    def learn_clause(self, clauses):
        return
    
    def make_decision(self):
        return
    
    def backjump(self):
        return    
          
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
    
    if len(sys.argv) != 2:
        print("Usage: py cdcl.py <filename.txt>")
        print("Where <filename.txt> is a CNF DIMACS equation")
        sys.exit(1)
    
    filename = sys.argv[1]
    cnf_formula = read_dimacs_file(filename)
    start_time = time.time()
    solver = CDCL()
    for clause in cnf_formula:
        solver.add_clause(clause)
    print(solver.get_literals())
    
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
    end_time = time.time()
    print("Time taken to solve:", end_time - start_time, "seconds")
    print("Assignment:", solver.assignment)
    print(solver.clauses)