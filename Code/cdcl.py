import sys
import time
import random

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
            # time.sleep(1)
            # print(self.decision_stack)
            unit_propagation_result = self.unit_propogation()
            # if (self.conflict_analysis()):
            #     print("conflict")
            #     if (self.decision_level == 0):
            #         return False
            #     self.backtack()
            if unit_propagation_result != "Done":
                new_clause = self.learn_clause(unit_propagation_result)
                self.backjump(new_clause)
                # print(self.decision_stack)
                # print(self.decision_level)
                print(new_clause)
                return False
            elif not self.get_unassigned_literals():
                return True
            else:
                self.make_decision()
                self.change_clause_states()
            
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
    
    def unit_propogation(self):
        last_clause = None
        while True:
            for clause in self.clauses:
                conflict = self.conflict_analysis()
                if conflict != False:
                    if last_clause == None:
                        return [clause, conflict]
                    else: 
                        return[last_clause, conflict]
                if self.clauses.get(clause) == "Unit":
                    self.assign_unit_clause(clause)
                if self.change_clause_states() == False:
                    return "Done"
                last_clause = clause
            
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
        # conflicting_clauses = []
        for clause in self.clauses:
            if self.clauses.get(clause) == "Conflict":
                # conflicting_clauses.append(clause)
                return clause
        # if conflicting_clauses == []:
        #     return False
        # else:
        #     print(conflicting_clauses)
        #     print(self.decision_stack)
        #     # print(self.decision_stack)
        #     # print(self.assignment)
        #     # print(self.get_clauses())
        #     return True
        return False
    
    def learn_clause(self, clauses):
        # print(clauses)
        conflicting_assignment = self.decision_stack[-1]
        # print(conflicting_assignment)
        conflicting_condition = self.get_cut_literals(conflicting_assignment[0])
        # print(conflicting_condition)
        learned_clause = []
        for literal in conflicting_condition:
            # print(literal)
            if literal[1] == False:
                learned_clause.append(literal[0])
            else:
                learned_clause.append(0 - literal[0])
        # print(learned_clause)
        self.add_clause(learned_clause)
        return learned_clause
            
    def get_cut_literals(self, assigned_literal):
        conflicting_condition_literals = []
        for implication in self.implication_graph:
            if assigned_literal in self.implication_graph[implication]:
                literal = implication
                assignment = self.assignment.get(literal)
                conflicting_condition_literals.append([literal, assignment])
        return conflicting_condition_literals

    def make_decision(self):
        unassigned_literals = self.get_unassigned_literals()
        if unassigned_literals:
            chosen_literal = random.choice(unassigned_literals)
            assignment = random.choice([True, False])
            self.assignment[chosen_literal] = assignment
            self.decision_stack.append((chosen_literal, assignment, self.decision_level, "Decision"))
            self.implication_graph[chosen_literal] = []
            print(f"Decision made: {chosen_literal} = {assignment} at level {self.decision_level}")
            self.decision_level += 1
    
    def backjump(self, learned_clause):
        print(learned_clause)
        print(self.decision_stack)
        print(self.implication_graph)
        for i in range(0, len(learned_clause)):
            learned_clause[i] = abs(learned_clause[i])
        decision_levels = []
        for d in self.decision_stack:
            if d[0] in learned_clause:
                decision_levels.append(d[2])
        print(decision_levels)
        second_highest_dl = 0
        highest_dl = 0
        if len(decision_levels) == 1:
            second_highest_dl = decision_levels[0]
        elif len(decision_levels) == 2:
            second_highest_dl = min(decision_levels)
        else:
            for x in decision_levels:
                print(x)
                if x > second_highest_dl:
                    second_highest_dl = x
                if x > highest_dl:
                    second_highest_dl = highest_dl
                    highest_dl = x
        print("SH: " , second_highest_dl)
        while True:
            decision = self.decision_stack[-1]
            print(decision)
            print(decision[2])
            print(decision[0])
            if decision[2] > second_highest_dl:
                self.decision_stack.pop()
                del self.assignment[decision[0]]
                temp = self.implication_graph
                for i in self.implication_graph:
                    if i == decision[0]:
                        del temp[decision[0]]
                    else:
                        if i in self.implication_graph[decision[0]]:
                            temp.remove(decision[0])
                self.implication_graph = temp
            else:
                break

          
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
    # print("Assignment:", solver.assignment)
    # print(solver.clauses)
    print("-----------------------------------------------------")
    print(solver.decision_stack)
    print(solver.implication_graph)