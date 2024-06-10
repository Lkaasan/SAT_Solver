import sys
import time
import random
from collections import deque

# class ImplicationGraph:
    
#     def __init__(self):

class CDCL:
    
    def __init__(self):
        self.literals = {}
        self.clauses = {}
        self.assignment = {}
        self.learned_clauses = []
        self.decision_stack = []
        self.decision_level = 0
        self.implication_graph = {}
    
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
            unit_propagation_result = self.unit_propogation()
            print(unit_propagation_result)
            if unit_propagation_result != "Done":
                if self.decision_stack[-1][2] == 0:
                    return False
                else:
                    if len(self.decision_stack) > 0:
                        self.decision_level += 1
                    new_clause = self.learn_clause(unit_propagation_result)
                    self.backjump(new_clause)
                    self.change_clause_states()
            elif self.check_finish():
                return True
            else:
                print("LOL", self.decision_level)
                if len(self.decision_stack) > 0:
                    self.decision_level += 1
                self.make_decision()
                self.change_clause_states()
                
    def check_finish(self):
        for x in self.clauses:
            if self.clauses[x] != 'Resolved':
                return False
        return True
            
    def change_clause_states(self):
        unit_change = False
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
                    self.clauses[clause] = "Unit"
                    unit_change = True
                elif self.check_conflict_clause(clause) == True:
                    self.clauses[clause] = "Conflict"
                else:
                    self.clauses[clause] = "Unresolved"
        return unit_change
        
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
    
    # def unit_propogation(self):
    #     last_clause = None
    #     while True:
    #         print(counter)
    #         for clause in self.clauses:
    #             conflict = self.conflict_analysis()
    #             print(conflict)
    #             if conflict != False:
    #                 if last_clause == None:
    #                     # return [clause, conflict]
    #                     return conflict
    #                 else: 
    #                     return conflict
    #                     # return[last_clause, conflict]
    #             if self.clauses.get(clause) == "Unit":
    #                 self.assign_unit_clause(clause)
    #                 break
    #             if self.change_clause_states() == False:
    #                 print(self.clauses)
    #                 return "Done"
    #             last_clause = clause
    #         counter += 1
    
    def unit_propogation(self):
        finish = False
        while True:
            for clause in self.clauses:
                conflict = self.conflict_analysis()
                if conflict != False:
                    return conflict
                else:
                    if self.clauses.get(clause) == "Unit":
                        self.assign_unit_clause(clause)
                        self.change_clause_states()
                        break
            return "Done"
            
    def assign_unit_clause(self, clause):
        implication = []
        l = None  

        for literal in clause:
            if abs(literal) not in self.assignment:
                assignment = literal > 0
                self.assignment[abs(literal)] = assignment
                l = abs(literal)
                self.decision_stack.append((abs(literal), assignment, self.decision_level, "Implication"))
            else:
                implication.append(abs(literal))

        if l is not None:
            if len(clause) == 1:
                self.implication_graph[abs(clause[0])] = []
            
            for x in implication:
                if x in self.implication_graph:
                    self.implication_graph[x].append(l)
                else:
                    self.implication_graph[x] = [l]
            self.implication_graph[l] = []
                
    def conflict_analysis(self):    
        for clause in self.clauses:
            if self.clauses.get(clause) == "Conflict":
                return clause
        return False
    
    def learn_clause(self, clause):
        conflicting_literal = self.decision_stack[-1][0]
        # included_variables = []
        # learned_clause = []
        # for x in clauses[0]:
        #     if abs(x) not in included_variables and abs(x) != conflicting_literal:
        #         included_variables.append(abs(x))
        #         learned_clause.append(x)
        # for x in clauses[1]:
        #     if abs(x) not in included_variables and abs(x) != conflicting_literal:
        #         included_variables.append(abs(x))
        #         learned_clause.append(x)        
        # if tuple(learned_clause) not in self.clauses:
        #     self.add_clause(learned_clause)
        # return learned_clause
        conflicting_decisions = self.get_cut_literals(clause)
        learned_clause = []
        for l in conflicting_decisions:
            if self.assignment[l] == False:
                learned_clause.append(l)
            else:
                learned_clause.append(0 - l)
        print(self.assignment)
        print(learned_clause)
        return learned_clause
                
                
            
    def get_cut_literals(self, clause):
        conflicting_condition_literals = []
        decisions = []
        for d in self.decision_stack:
            if d[3] == 'Decision':
                decisions.append(d[0])
        for literal in clause:
            l = abs(literal)
            queue = deque()
            queue.append(l)
            while len(queue) != 0:
                for x in range(0, len(queue)):
                    temp = queue.popleft()
                    if temp in decisions and temp not in conflicting_condition_literals:
                        conflicting_condition_literals.append(temp)
                    else:
                        print(self.implication_graph)
                        for i in self.implication_graph:
                            if temp in self.implication_graph[i]:
                                queue.append(i)
        print("conflicting decisions: ", conflicting_condition_literals)
        return conflicting_condition_literals
                            
    def make_decision(self):
        unassigned_literals = self.get_unassigned_literals()
        if unassigned_literals:
            chosen_literal = random.choice(unassigned_literals)
            assignment = random.choice([True, False])
            self.assignment[chosen_literal] = assignment
            self.decision_stack.append((chosen_literal, assignment, self.decision_level, "Decision"))
            self.implication_graph[chosen_literal] = []
            # print(f"Decision made: {chosen_literal} = {assignment} at level {self.decision_level}")

    def backjump(self, learned_clause):
        if len(learned_clause) == 1:
            self.implication_graph = []
            self.assignment = {}
            self.decision_stack = []
        else:
            for i in range(0, len(learned_clause)):
                learned_clause[i] = abs(learned_clause[i])
            decision_levels = []
            for d in self.decision_stack:
                if d[0] in learned_clause:
                    decision_levels.append(d[2])
            second_highest_dl = 0
            highest_dl = 0
            if len(decision_levels) == 1:
                second_highest_dl = decision_levels[0]
            elif len(decision_levels) == 2:
                second_highest_dl = min(decision_levels)
            else:
                for x in decision_levels:
                    if x > highest_dl:
                        second_highest_dl = highest_dl
                        highest_dl = x
            print(decision_levels)
            print("SH: " , second_highest_dl)
            print("decision levels: ", self.decision_level)
            if second_highest_dl == self.decision_stack[-1][2]:
                second_highest_dl -= 1
            elif max(decision_levels) == min(decision_levels) and second_highest_dl != 0:
                second_highest_dl = max(decision_levels) - 1
            if second_highest_dl == 0:
                self.implication_graph = []
                self.assignment = {}
                self.decision_stack = []
            else:
                while True:
                    decision = self.decision_stack[-1]
                    if decision[2] > second_highest_dl:
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
                self.decision_level = second_highest_dl
                print(self.decision_stack)
          
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
    print("-----------------------------------------------------")
    print(solver.decision_stack)
    # print(solver.implication_graph)