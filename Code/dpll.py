#DPLL SAT Solver for Imbalanced Instances - Lukas Kaas Andersen

import sys
import time
import random
import threading

class DPLL:
    
    #Constructor: creating data structures
    def __init__(self):
        self.literals = {}
        self.clauses = {}
        self.assignment = {}
        self.literals_polarities = {}
        self.pure_literals = []

    #Function that adds a clause, and ammends literal occurrences
    #@param clause: clause to be added
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

    #Function that returns the clause dictionary
    #@return: clause dictionary
    def get_clauses(self):
        return self.clauses
        
    #Function that returns the literal dictionary
    #@return: literal dictionary
    def get_literals(self):
        return self.literals
        
    #Function that returns the assignment dictionary
    #@return: assignment dictionary
    def get_assignment(self):
        return self.assignment
    
    #Function that returns the literal polarities dictionary
    #@return: literal polarities dictionary
    def get_literals_polarities(self):
        return self.literals_polarities
        
    #Recursive function that carries out dpll
    #@return: SAT/UNSAT (True/False)
    def dpll(self):
        #Check if current assignment is SAT
        if self.check_satisfiability():
            return True
        #Checks for conflict, backtrack if true
        elif self.check_conflict():
            return False
        else: 
            #Checks if pure literals still need to be assigned
            if bool(self.pure_literals) is True:
                pure_literal = self.pure_literals.pop()
                if pure_literal < 0:
                    self.assignment[abs(pure_literal)] = False
                else:
                    self.assignment[pure_literal] = True
                #Recursive call
                if self.dpll():
                    return True
                else:
                    del self.assignment[abs(pure_literal)]
            #Checks if there is a unit clause to be propagated
            unit_clause_literal = self.find_unit_clause_literal()  
            if unit_clause_literal is not False:
                #Assigns the unit clause literal appropriately
                if unit_clause_literal < 0:
                    self.assignment[abs(unit_clause_literal)] = False
                else:
                    self.assignment[unit_clause_literal] = True
                #Recursive call
                if self.dpll():
                    return True
                else:
                    del self.assignment[abs(unit_clause_literal)]
            
            #Gets next literal to be assigned
            literal = self.choose_literal([])
            
            #If no literal to be assigned
            if literal is None:
                return False

            #Assigns chosen literal depending on literal polarity
            if self.literals_polarities.get(literal) > self.literals_polarities.get(0 - int(literal)):
                assignment = True
            else:
                assignment  = False
    
            self.assignment[literal] = assignment
            
            #Recursive call
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]
            
            #Try's other assignment if backtrack occurs
            self.assignment[abs(literal)] = not assignment
            
            #Recursive call
            if self.dpll():
                return True
            else:
                del self.assignment[abs(literal)]
        return False
    
    #Function that checks for conflicts
    #@return: True if conflict detected, false otherwise
    def check_conflict(self):
        for clause in self.clauses:
            assigned_literal = 0 
            all_false_checker = True
            for index, literal in enumerate(clause):
                if abs(literal) in self.assignment:
                    assigned_literal += 1
                    if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                        all_false_checker = False
            #If all literals in clause have been assigned and all evaluate to false
            if assigned_literal == len(clause) and all_false_checker == True:
                return True
        return False
            
    #Function that chooses a literal to be assigned
    #@param: literals, list of literals to decide between, can be an empty list
    #@return: chosen literal to be assigned 
    def choose_literal(self, literals):
        #If it is a normal decision between unassigned literals
        if literals == []:
            
            #Return literal with max occurrences
            unassigned_literals = [l for l in self.literals if l not in self.assignment]
            max_literal = max(unassigned_literals, key=self.literals.get)
            max_value = self.literals.get(max_literal)
            max_variables = [l for l in unassigned_literals if self.literals.get(l) == max_value]
            return random.choice(max_variables)
        
        #If literals have been input through the param (One-off unit clauses)
        elif literals != []:
            
            #Return literal with max occurrences from the literals param
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
    
    #Function that finds a literal from either a unit clause or one off unit clause
    #@return: literal to be assigned, or false if no unit or one off unit clauses
    def find_unit_clause_literal(self):
        unit_literals = []
        one_off_unit_literals = []
        
        #Populates lists in for loop
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
                            one_off_unit_literals.append(abs(literal))
        
        #Return random choice from unit literals to be assigned
        if unit_literals != []:
            return random.choice(unit_literals)
        
        #If no unit literals, call choose_literal() and return one off unit literal to be assigned
        elif one_off_unit_literals != []:
            return self.choose_literal(one_off_unit_literals)
        
        #Return false otherwise
        else:
            return False
        
    #Function that populates all pure literals in the formula
    def populate_pure_literal(self):
        for literal in self.literals:
            positive_literal = self.literals_polarities.get(literal)
            negative_literal = self.literals_polarities.get(0 - literal)
            
            #Adds if literal only appears in one polarity
            if (positive_literal == 0 and negative_literal != 0):
                self.pure_literals.append(0 - literal)
            elif (positive_literal != 0 and negative_literal == 0):
                self.pure_literals.append(literal)
                
        #Includes 1 length clauses
        for c in self.clauses:
            if len(c) == 1:
                self.pure_literals.append(c[0])
            
    #Function that checks satisfiability, and ammends clauses status and literal occurrences
    #@return: SAT/UNSAT (True/False)
    def check_satisfiability(self):
        r = True
        
        #Loops through each clause 
        for clause in self.clauses:
            clause_satisfied = False
            
            #Checks if clause is now resolved, and ammends data appropriately
            for literal in clause:
                if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                    clause_satisfied = True
                    if self.clauses[clause] != "Resolved":
                        for l in clause:
                            self.literals[abs(l)] -= 1
                        self.clauses[clause] = "Resolved"
                    break
                    
            #If clause is not resolved
            if not clause_satisfied:
                
                #If clause is unit clause
                if self.check_unit_clause(clause):
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "Unit"
                    
                #If clause is one off unit clause
                elif self.check_close_unit_clause(clause):
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "One Off Unit"

                #If clause was resolved and now is unresolved due to backtracking
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
        
    #Function that checks if a clause is a unit clause
    #@param: clause to be checked
    #@return: true if unit, false otherwise
    def check_unit_clause(self, clause):
        assigned_variables = 0
        for literal in clause:
            if abs(literal) in self.assignment:
                assigned_variables += 1
        if assigned_variables == len(clause) - 1:
            return True
        else:
            return False
                
    #Function that checks if a clause is a one off unit clause
    #@param: clause to be checked
    #@return: true if one off unit, false otherwise
    def check_close_unit_clause(self, clause):
        assigned_variables = 0
        for literal in clause:
            if abs(literal) in self.assignment:
                assigned_variables += 1
        if assigned_variables == len(clause) - 2:
            return True
        else:
            return False
         
#Function that reads a DIMACS CNF file
#@param: filename of the file to be read
#@return: a list of clauses
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
    #Checks for corrent number of arguments
    if len(sys.argv) != 2:
        print("Usage: py sat_solver.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    #Read CNF
    cnf = read_dimacs_file(filename)
    solver = DPLL()
    
    #Add clauses to solver and populate pure literals 
    for clause in cnf:
        solver.add_clause(clause)
    solver.populate_pure_literal()
        
    #Start timer
    start_time = time.time()
    
    #Solve and print appropriately
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
    end_time = time.time()
    print("Time taken to solve: ", end_time - start_time, "seconds")
    print("Assignment: ", solver.get_assignment())