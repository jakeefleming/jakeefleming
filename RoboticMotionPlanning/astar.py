from RobotPlanningSolution import RobotPlanningSolution
from heapq import heappush, heappop


class AstarNode:
    # each search node except the root has a parent node
    # and all search nodes wrap a state object

    def __init__(self, state, heuristic, parent=None, transition_cost=0):
        # you write this part
        self.state = state
        self.heuristic = heuristic
        self.parent = parent
        self.transition_cost = transition_cost

    def priority(self):
        return self.heuristic + self.transition_cost

    # comparison operator,
    # needed for heappush and heappop to work with AstarNodes:
    def __lt__(self, other):
        return self.priority() < other.priority()


# take the current node, and follow its parents back
#  as far as possible. Grab the states from the nodes,
#  and reverse the resulting list of states.
def backchain(node):
    result = []
    current = node
    while current:
        result.append(current.state)
        current = current.parent

    result.reverse()
    return result


def astar_search(search_problem, heuristic_fn):
    start_state_tuple = tuple(search_problem.start_state)  # convert list to tuple
    start_node = AstarNode(start_state_tuple, heuristic_fn(start_state_tuple))

    pqueue = []
    heappush(pqueue, start_node)

    solution = RobotPlanningSolution(search_problem, "Astar with heuristic " + heuristic_fn.__name__)

    # create set and dictionary
    explored = set()
    visited_cost = {start_state_tuple: 0}

    # while pq is not empty
    while len(pqueue) > 0:
        # extract
        curr = heappop(pqueue)

        # check for goal
        if search_problem.is_goal(curr.state):
            solution.cost = curr.transition_cost
            solution.path = backchain(curr)
            return solution

        # visit
        explored.add(curr.state)
        solution.nodes_visited += 1

        # get successors
        for successor in search_problem.get_successors(curr.state):
            successor_tuple = tuple(successor)  # convert list to tuple
            transition_cost = curr.transition_cost + 1
            next_node = AstarNode(successor_tuple, heuristic_fn(successor_tuple), curr, transition_cost)

            # if not explored, add it to pq
            if successor_tuple not in explored:
                visited_cost[successor_tuple] = next_node.priority()
                heappush(pqueue, next_node)

            # if explored, but found with better score, add it to pq
            elif visited_cost[successor_tuple] > next_node.priority():
                visited_cost[successor_tuple] = next_node.priority()
                heappush(pqueue, next_node)

    # return
    return solution

