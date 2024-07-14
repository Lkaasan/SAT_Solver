#CDCL SAT Solver for Imbalanced Instances - Lukas Kaas Andersen

import sys
import time
import random
from collections import deque

class CDCL:
    
    #Constructor that sets all variables and data structues
    #@param heuristic, whether to run CDCL with heuristic or not
    def __init__(self, heuristic):
        self.literals = {}
        self.clauses = {}
        self.assignment = {}
        self.decision_stack = []
        self.decision_level = 0
        self.implication_graph = {}
        self.literals_polarities = {}
        if heuristic == True:
            self.heuristic = True
        else:
            self.heuristic = False
    
    #Function that adds a clause, and ammends literal occurrences
    #@param clause: clause to be added
    def add_clause(self, clause):
        if len(clause) == 1:
            self.clauses[tuple(clause)] = "Unit"
        else:
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

    #Function that returns the literal polarities dictionary
    #@return: literal polarities dictionary    
    def get_literal_polarities(self):
        return self.literals_polarities
    
    #Function that returns the assignment dictionary
    #@return: assignment dictionary
    def get_assignment(self):
        return self.assignment
    
    #Function that returns the decision stack
    #@return: decision stack
    def get_decision_stack(self):
        return self.decision_stack
    
    #Function that gets unassigned literals
    #@return: list of unassigned literals
    def get_unassigned_literals(self):
        return [literal for literal in self.literals if literal not in self.assignment]
    
    #Function for the main dpll loop
    #@return: SAT/UNSAT (True/False)
    def dpll(self):
        while True:
            #changes clause states and starts unit propagation
            self.change_clause_states()
            unit_propagation_result = self.unit_propagation()
            
            #If conflict detected
            if unit_propagation_result != "Done":
                
                #If contflict occurred on decision level 0, UNSAT
                if self.decision_stack[-1][2] == 0:
                    return False
                else:
                    
                    #learned new clause and backjump appropriately
                    if len(self.decision_stack) > 0:
                        self.decision_level += 1
                    new_clause = self.learn_clause(unit_propagation_result)
                    self.backjump(new_clause)
                    self.change_clause_states()
                    
            #Checks if SAT
            elif self.check_finish():
                return True
            
            #Otherwise, make a decision
            else:
                if len(self.decision_stack) > 0:
                    self.decision_level += 1
                self.make_decision()
                self.change_clause_states()
    
    #Function that checks for SAT
    #@return: True if SAT, False otherwise
    def check_finish(self):
        for x in self.clauses:
            if self.clauses[x] != 'Resolved':
                return False
        return True
            
    #Function that updates clause status and literal occurrences
    def change_clause_states(self):
        for clause in self.clauses:
            clause_satisfied = False
            
            #Checks if clause is now resolved
            for literal in clause:
                if (literal > 0 and self.assignment.get(abs(literal)) is True) or (literal < 0 and self.assignment.get(abs(literal)) is False):
                    clause_satisfied = True
                    if self.clauses[clause] != "Resolved":
                        for l in clause:
                            self.literals[abs(l)] -= 1
                        self.clauses[clause] = "Resolved"
                    break
            if not clause_satisfied:
                
                #Checks if clause is a unit clause
                if self.check_unit_clause(clause):
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "Unit"
                    
                #Checks if clause is a conflicting
                elif self.check_conflict_clause(clause) == True:
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "Conflict"
                    
                #Checks if clause was resolved and is now unresolved due to backjumping
                else:
                    if self.clauses[clause] == "Resolved":
                        for l in clause:
                            self.literals[abs(l)] += 1
                    self.clauses[clause] = "Unresolved"
    
    #Function that checks if a clause is conflicting
    #@param: clause to be checked
    #@return; True if clause is conflicting, false otherwise
    def check_conflict_clause(self, clause):
        assigned_variables = 0
        for l in clause:
            if abs(l) in self.assignment:
                assigned_variables += 1
        if assigned_variables == len(clause):
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
    
    #Function that performs unit propagation
    #@return: "Done" if no conflicts were found and propagation is finished, conflicting clause if one is found
    def unit_propagation(self):
        while True:
            found_unit = False
            for clause in self.clauses:
                
                #Checks for conflict
                conflict = self.conflict_analysis()
                if conflict != False:
                    return conflict  

                #If clause is unit, make assignments and restart loop
                if self.clauses[clause] == "Unit":
                    self.assign_unit_clause(clause)
                    self.change_clause_states()
                    found_unit = True
                    break
            if found_unit == False:
                return "Done"
            
    #Function that assigns a unit clause
    #@param clause to be assigned
    def assign_unit_clause(self, clause):
        implication = []
        l = None  
        
        #Assigns the unit clause appropriately and adds to the decision stack as an implication
        for literal in clause:
            if abs(literal) not in self.assignment:
                assignment = literal > 0
                self.assignment[abs(literal)] = assignment
                l = abs(literal)
                self.decision_stack.append((abs(literal), assignment, self.decision_level, "Implication"))
            else:
                implication.append(abs(literal))

        #Updates the implication graph appropriately
        if l is not None:
            if len(clause) == 1:
                self.implication_graph[abs(clause[0])] = []
            
            for x in implication:
                if x in self.implication_graph:
                    self.implication_graph[x].append(l)
                else:
                    self.implication_graph[x] = [l]
            self.implication_graph[l] = []

    #Function that checks for a conflict
    #@return: conflicting clause, or False if non is found
    def conflict_analysis(self):    
        for clause in self.clauses:
            if self.clauses.get(clause) == "Conflict":
                return clause
        return False
    
    #Function that learns a new clause
    #@param: conflicting clause
    #@return: new learned clause
    def learn_clause(self, clause):
        
        #gets decisions that led to the conflict
        conflicting_decisions = self.get_cut_literals(clause)
        learned_clause = []
        
        #loops through all decisions added and reverses the assignments
        for l in conflicting_decisions:
            if self.assignment[l] == False:
                learned_clause.append(l)
            else:
                learned_clause.append(0 - l)
        
        #adds new learned clause to solver
        self.add_clause(learned_clause)
        return learned_clause

    #Function that gets decisions that lead to the conflict
    #@param: conflicting clause
    #@return: list of decisions
    def get_cut_literals(self, clause):
        conflicting_condition_literals = []
        decisions = []
        
        #gets all decisions from current search path
        for d in self.decision_stack:
            if d[3] == 'Decision':
                decisions.append(d[0])
                
        #loops through each literal in conflicting clause and performs a DFS on implication graph to find decisions
        for literal in clause:
            l = abs(literal)
            
            #Create a queue
            queue = deque()
            queue.append(l)
            
            #DFS search
            while len(queue) != 0:
                for x in range(0, len(queue)):
                    temp = queue.popleft()
                    if temp in decisions and temp not in conflicting_condition_literals:
                        conflicting_condition_literals.append(temp)
                    else:
                        for i in self.implication_graph:
                            if temp in self.implication_graph[i]:
                                queue.append(i)
        return conflicting_condition_literals
    
    #Function that makes a decision on what literal to assign next                      
    def make_decision(self):
        
        #get unassigned literals
        unassigned_literals = self.get_unassigned_literals()
        if unassigned_literals:
            
            #If solver run without heuristic (random decision and assignment)
            if self.heuristic == False:
                chosen_literal = random.choice(unassigned_literals)
                assignment = random.choice([True, False])

            #Decision and assignment with heuristic
            else:
                chosen_literal, assignment = self.make_choice_with_heuristic(unassigned_literals)
                
            #add assignment, and update decision stack and implication graph
            self.assignment[chosen_literal] = assignment
            self.decision_stack.append((chosen_literal, assignment, self.decision_level, "Decision"))
            self.implication_graph[chosen_literal] = []
    
    #Function that makes a decision and assignment with the DLIS decision heuristic
    #@return: literal and assigment
    def make_choice_with_heuristic(self, unassigned_literals):
        max_literals = []
        max_occurrence = 0
        
        #Gets literal with highest occurrence in unresolved clauses
        for l in unassigned_literals:
            occurrence = self.literals.get(abs(l))
            if occurrence > max_occurrence:
                max_literals = []
                max_literals.append(l)
                max_occurrence = occurrence
            elif occurrence == max_occurrence:
                max_literals.append(l)
        decision = random.choice(max_literals)
        
        #Makes assignment based on literal polarity occurrences
        if self.literals_polarities[decision] > self.literals_polarities[0 - decision]:
            assignment = True
        else:
            assignment = False
        return decision, assignment

    #Function that backjump depending on learned clause, and edits data structure appropriately
    def backjump(self, learned_clause):
        
        #If learned clause is unit, restart search and reset data structures
        if len(learned_clause) == 1:
            self.implication_graph.clear()
            self.assignment.clear()
            self.decision_stack.clear()
            self.decision_level = 0
        else:
            
            #Get decision levels of learned clause
            for i in range(0, len(learned_clause)):
                learned_clause[i] = abs(learned_clause[i])
            decision_levels = []
            for d in self.decision_stack:
                if d[0] in learned_clause:
                    decision_levels.append(d[2])
                    
            #Find second highest decision level in learned clause
            second_highest_dl = 0
            highest_dl = 0
            
            #If only one decision level
            if len(decision_levels) == 1:
                second_highest_dl = decision_levels[0]
                
            #If there are two decision levels, take the min
            elif len(decision_levels) == 2:
                second_highest_dl = min(decision_levels)
                
            #If all decision levels are the same (max = min)
            elif max(decision_levels) == min(decision_levels):
                second_highest_dl = max(decision_levels) - 1
                
            #Otherwise, calculate second highest
            else:
                for x in decision_levels:
                    if x > highest_dl:
                        second_highest_dl = highest_dl
                        highest_dl = x
                        
            #If second highest decisiol level is 0, restart search and reset data structures
            if second_highest_dl == 0:
                self.implication_graph.clear()
                self.assignment.clear()
                self.decision_stack.clear()
                self.decision_level = 0
                
            #Otherwise, remove appropriate data from decision stack and implication graph
            else:
                while True:
                    decision = self.decision_stack[-1]
                    if decision[2] >= second_highest_dl:
                        self.decision_stack.pop()
                        del self.assignment[decision[0]]
                        temp = self.implication_graph
                        for i in self.implication_graph:
                            if decision[0] in self.implication_graph[i]:
                                temp[i].remove(decision[0])
                        temp.pop(decision[0])
                        self.implication_graph = temp
                    else:
                        break
            if second_highest_dl != 0: 
                self.decision_level = second_highest_dl - 1

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
    if len(sys.argv) != 4 and (sys.argv[2] != "h" or sys.argv[2] != "nh"):
        print("Usage: python3 cdcl.py <filename.txt> <h/nh> <repetitions>")
        print("Where <filename.txt> is a CNF DIMACS equation and <h/nh> is heuristic/no heuristic and <repetitions> is how many times it should run")
        sys.exit(1)
    
    filename = sys.argv[1]
    cnf_formula = read_dimacs_file(filename)
    repetitions = sys.argv[3]
    total_time = 0.0
    
    #Run solver the amount of times inputted by the user
    for i in range (0, int(repetitions)):
        
        #Create solver ran with heuristic
        if sys.argv[2]  == "h":
            solver = CDCL(True)
            
        #Create solver ran without heuristic
        else:
            solver = CDCL(False)
            
        #Add clauses
        for clause in cnf_formula:
            solver.add_clause(clause)
            
        #Start timer
        start_time = time.time()
        
        #Solver and print appropriately
        if solver.dpll():
            print("Satisfiable")
        else:
            print("Unsatisfiable")
        end_time = time.time()
        time_taken = end_time - start_time
        total_time += time_taken
        print("Time taken to solve:", end_time - start_time, "seconds")
        print("Assignment:", solver.get_assignment())
        print("-----------------------------------------------------")
        print("Decision Stack: ", solver.get_decision_stack())
        print("-----------------------------------------------------")
    print("Average time: ", total_time / float(repetitions))

    