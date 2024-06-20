# Author: Jake Fleming

import math

# calculate distance between two angles (considering 2pi and 0 the same)
def angular_distance(a1, a2):
    p = abs(a1 - a2) % (math.pi * 2)
    return min(p, (math.pi * 2) - p)

class RobotPlanningProblem:
    # store all important pieces of graph
    def __init__(self, vertices, edges, start_state, goal_state, state_to_index, link_lengths):
        self.vertices = vertices
        self.edges = edges
        self.start_state = start_state
        self.goal_state = goal_state
        self.state_to_index = state_to_index
        self.link_lengths = link_lengths

    # using the sum of all angular distances heuristic for each angle
    def heuristic_fn(self, state):
        return sum([angular_distance(state[i], self.goal_state[i]) for i in range(len(state))])

    # return the tuple of each neighbor of a passed configuration
    def get_successors(self, state):
        index = self.state_to_index[state]
        return [tuple(self.vertices[i]) for i in self.edges[index]]

    # check if goal is reached
    def is_goal(self, state):
        return self.goal_state == state
