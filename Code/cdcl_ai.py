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

    def add_clause(self, clause):
        self.clauses[tuple(clause)] = "Unresolved"
        for literal in clause:
            if literal not in self.literals:
                self.literals[literal] = set()
            self.literals[literal].add(tuple(clause))

    def get_unassigned_literals(self):
        return [literal for literal in self.literals if literal not in self.assignment]

    def get_decision_literal(self):
        return random.choice(self.get_unassigned_literals())

    def propagate_unit_clauses(self):
        unit_literals = [literal for literal in self.assignment if len(self.literals[-literal] - set(self.learned_clauses)) == 0]
        for literal in unit_literals:
            self.assignment[literal] = True
            self.decision_stack.append(literal)
            conflicting_literal = self.propagate()
            if conflicting_literal:
                return conflicting_literal
        return None

    def propagate(self):
        while self.decision_stack:
            literal = self.decision_stack.pop()
            for clause in self.literals[-literal] - set(self.learned_clauses):
                unresolved_literal = None
                for l in clause:
                    if l in self.assignment:
                        if self.assignment[l]:
                            break
                    else:
                        if unresolved_literal is None:
                            unresolved_literal = l
                        else:
                            unresolved_literal = None
                            break
                if unresolved_literal is None:
                    return literal
                else:
                    self.assignment[unresolved_literal] = False
                    self.decision_stack.append(unresolved_literal)
        return None

    def learn_clause(self, conflicting_literal):
        learned_clause = [conflicting_literal]
        implied_literals = set()
        for literal in reversed(self.decision_stack):
            if literal == conflicting_literal:
                break
            learned_clause.append(literal)
            implied_literals.add(-literal)
        self.learned_clauses.append(tuple(learned_clause))
        for literal in implied_literals:
            if literal not in self.literals:
                self.literals[literal] = set()
            self.literals[literal].add(tuple(learned_clause))

    def backtrack(self):
        while self.decision_stack:
            literal = self.decision_stack.pop()
            if -literal in self.assignment:
                del self.assignment[-literal]
                return literal
        return None

    def dpll(self):
        conflicting_literal = self.propagate_unit_clauses()
        while conflicting_literal is not None:
            self.learn_clause(conflicting_literal)
            backtrack_literal = self.backtrack()
            if backtrack_literal is None:
                return False
            self.decision_stack.append(backtrack_literal)
            conflicting_literal = self.propagate()
        if not self.get_unassigned_literals():
            return True
        decision_literal = self.get_decision_literal()
        self.assignment[decision_literal] = True
        self.decision_stack.append(decision_literal)
        return self.dpll()

if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) != 2:
        print("Usage: python cdcl_solver.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    cnf_formula = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('c') or line.startswith('p') or line.startswith('%') or line.startswith('0'):
                continue  
            clause = [int(x) for x in line.strip().split() if x != '0']
            if clause:
                cnf_formula.append(clause)
                
    solver = CDCL()
    print(cnf_formula)
    for clause in cnf_formula:
        solver.add_clause(clause)

    print(solver.literals)
    
    if solver.dpll():
        print("Satisfiable")
    else:
        print("Unsatisfiable")
    
    end_time = time.time()
    print("Time taken to solve:", end_time - start_time, "seconds")
    print("Assignment:", solver.assignment)
    print(solver.clauses)