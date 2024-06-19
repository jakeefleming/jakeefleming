# Author: Jake Fleming

import random, math


class SAT:
    def __init__(self, filename):
        self.model = []
        self.new_variables = {}     # map old to new
        self.old_variables = {}     # map new to old
        self.variable_values = {}   # map new to boolean

        # read the cnf file and assign each variable to a corresponding integer starting at 1 (generalization)
        file = open(filename, "r")
        new_var = 1
        for line in file:
            line = line.strip()
            clause = []
            for var in line.split(" "):
                if var[0] != "-":
                    if var not in self.new_variables:
                        # add variable to dicts
                        self.new_variables[var] = new_var
                        self.old_variables[new_var] = var
                        clause.append(new_var)
                        new_var += 1
                    else:
                        # otherwise, reuse
                        clause.append(self.new_variables[var])
                else:
                    neg_variable = var[1:]
                    if neg_variable not in self.new_variables:
                        # add variable to dicts
                        self.new_variables[neg_variable] = new_var
                        self.old_variables[new_var] = neg_variable
                        new_var += 1
                    # add positive version to clause
                    clause.append((-1) * self.new_variables[neg_variable])
            # make model out of each clause
            self.model.append(clause)

        file.close()

    # assign random boolean to each variable when asked
    def random_assignment(self):
        for var in self.old_variables:
            self.variable_values[var] = bool(random.getrandbits(1))

    # goal test checks if at least one variable matches its assignment in every clause
    def goal_test(self):
        for clause in self.model:
            clause_value = False
            for variable in clause:
                # if positive and true
                if variable > 0 and self.variable_values[variable]:
                    clause_value = True
                # if negative and false
                elif variable < 0 and not self.variable_values[(-1) * variable]:
                    clause_value = True
            if not clause_value:
                return False

        return True

    # helper function to flip random variable with the flip that would make the most clauses true
    def flip_highest_variable(self, candidate):
        # keep track of each flip and its score
        successor_score = {}
        highest_score = 0
        for var in candidate:
            # flip for check
            self.variable_values[var] = not self.variable_values[var]
            score = self.score()
            successor_score[var] = score
            # update the highest score
            if score > highest_score:
                highest_score = score
            # flip back
            self.variable_values[var] = not self.variable_values[var]

        # get all best variables for random selection
        best_variables = []
        for successor in successor_score:
            if successor_score[successor] == highest_score:
                best_variables.append(successor)

        random_var = random.choice(best_variables)
        self.variable_values[random_var] = not self.variable_values[random_var]

    # count every True clause using same logic as goal test
    def score(self):
        count = 0
        for clause in self.model:
            clause_value = False
            for variable in clause:
                if variable > 0 and self.variable_values[variable]:
                    clause_value = True
                elif variable < 0 and not self.variable_values[(-1) * variable]:
                    clause_value = True
            if clause_value:
                count += 1

        return count

    # for walk_sat, get a list of all unsatisfied clauses using the same logic as goal test
    def unsatisfied_clauses(self):
        unsatisfied = []
        for clause in self.model:
            clause_value = False
            for variable in clause:
                if variable > 0 and self.variable_values[variable]:
                    clause_value = True
                elif variable < 0 and not self.variable_values[(-1) * variable]:
                    clause_value = True

            # add false clauses to list
            if not clause_value:
                unsatisfied.append(clause)

        return unsatisfied

    # algorith that solves problem, h is our probability constant and max_iterations is where we decide to give up
    def gsat(self, h, max_iterations):
        # call random assignment
        self.random_assignment()
        iterations = 0
        # loop until goal is found or we give up
        while not self.goal_test() and iterations < max_iterations:
            iterations += 1
            # check random number with h
            number = random.uniform(0, 1)
            if number > h:
                # flip random variable
                random_variable = random.choice(list(self.variable_values.keys()))
                self.variable_values[random_variable] = not self.variable_values[random_variable]
            else:
                # flip best variable otherwise
                self.flip_highest_variable(self.variable_values)

        # print attempts and return True so it can write solution
        print(iterations)
        return True

    # similar to gsat but improved runtime because of unsatisfied clause search
    def walk_sat(self, h, max_iterations):
        # make random assignment
        self.random_assignment()
        iterations = 0
        # loop until goal or give up
        while not self.goal_test() and iterations < max_iterations:
            iterations += 1
            # compare random number with h
            number = random.uniform(0, 1)
            if number > h:
                # flip random variable
                random_variable = random.choice(list(self.variable_values.keys()))
                self.variable_values[random_variable] = not self.variable_values[random_variable]
            else:
                # pick a random unsatisfied clause
                candidate = random.choice(self.unsatisfied_clauses())
                candidate = [abs(i) for i in candidate]   # need positive variables without changing lists in model
                self.flip_highest_variable(candidate)

        # print attempts and return true
        print(iterations)
        return True

    # additional walk algorithm to solve some puzzles, takes parameters of temperatures and cooling rates to determine
    # Probabilities and when the loop should end
    def simulated_annealing(self, initial_temperature, cooling_rate, min_temp):
        # make random assignment
        self.random_assignment()
        current_temp = initial_temperature
        current_score = self.score()
        # loop until goal found or temp is too low
        while not self.goal_test() and current_temp > min_temp:
            # flip random variable and score it
            random_variable = random.choice(list(self.variable_values.keys()))
            self.variable_values[random_variable] = not self.variable_values[random_variable]
            new_score = self.score()

            # find difference from original
            delta_score = current_score - new_score
            # include this to avoid error with math.exp overflow math range
            if delta_score > 15 * current_temp:
                acceptance_probability = 0
            # find probability by comparing with temp and score
            else:
                acceptance_probability = math.exp(delta_score / current_temp)

            # update if better score or we pass acceptance probability
            if new_score > current_score or random.uniform(0, 1) < acceptance_probability:
                current_score = new_score
            else:
                # revert the flip if not accepted
                self.variable_values[random_variable] = not self.variable_values[random_variable]

            # lower temp
            current_temp *= cooling_rate

        print(current_temp)
        return True

    # write a .sol file for solution
    def write_solution(self, filename):
        file = open(filename, "w")
        for var in self.variable_values:
            # if true write it positive
            if self.variable_values[var]:
                s = self.old_variables[var]
            # if false write it negative
            else:
                s = '-' + self.old_variables[var]
            file.writelines(s + "\n")
        file.close()