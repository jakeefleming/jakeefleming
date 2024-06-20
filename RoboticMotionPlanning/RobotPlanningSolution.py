# Author: Jake Fleming

# store important information for A* search
class RobotPlanningSolution:
    def __init__(self, problem, search_method):
        self.problem_name = str(problem)
        self.search_method = search_method
        self.path = []
        self.nodes_visited = 0
        self.cost = 0
