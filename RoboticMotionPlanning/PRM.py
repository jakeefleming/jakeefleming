# Author: Jake Fleming

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from astar import astar_search
from RobotPlanningProblem import RobotPlanningProblem
import math


# find the locations of the points on the arm using sin and cos
def compute_end_points(angles, link_lengths):
    x, y = 0, 0
    points = [(x, y)]
    theta = 0

    # each step builds off of the previous
    for i in range(len(angles)):
        theta += angles[i]
        x += link_lengths[i] * np.cos(theta)
        y += link_lengths[i] * np.sin(theta)
        points.append((x, y))

    return points

# use our matplotlib to draw an arm
def draw_robot_arm(points, color):
    for i in range(len(points) - 1):
        plt.plot([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], color)

# show the grid
def show_plot():
    plt.axis('equal')
    plt.grid(True)
    plt.show()

# given angles, check if the arm collides with an obstacle
def check_collision(arm_angles, obstacles, link_lengths):
    # convert to points
    arm_points = compute_end_points(arm_angles, link_lengths)
    arm_line = LineString(arm_points)

    # check for each obstacle
    for obstacle in obstacles:
        if arm_line.intersects(obstacle):
            return True

    return False

# create all the vertices for our graph - num_samples refers to how many vertices we wish to use (density of graph)
def sample_configurations(space_bounds, num_samples, obstacles, link_lengths):
    configurations = []

    for i in range(num_samples):
        # get random angles
        configuration = [np.random.uniform(low, high) for low, high in space_bounds]

        # check for collision
        if not check_collision(configuration, obstacles, link_lengths):
            configurations.append(configuration)

    return configurations

# calculate distance between two angles (considering 2pi and 0 the same)
def angular_distance(a1, a2):
    p = abs(a1 - a2) % (math.pi * 2)
    return min(p, (math.pi * 2) - p)

# return the k closest vertices by indices
def connect_vertices(vertex, vertices, k):
    # we are using the sum of angular distances for each angle as heuristic
    distances = [sum([angular_distance(vertex[i], v[i]) for i in range(len(vertex))]) for v in vertices]
    sorted_indices = np.argsort(distances)
    return sorted_indices[1:k + 1]  # exclude the first index as it is the vertex itself

# create the graph and use our old A* search to find solution
def prm_planner(start_config, goal_config, obstacles, space_bounds, link_lengths, num_samples, k):
    # create all the vertices
    vertices = sample_configurations(space_bounds, num_samples, obstacles, link_lengths)
    vertices.append(start_config)
    vertices.append(goal_config)

    # create all the edge lists
    edges = {i: [] for i in range(len(vertices))}

    # for each vertex, create an edge between the k closest vertices
    for i, vertex in enumerate(vertices):
        neighbors_indices = connect_vertices(vertex, vertices, k)
        for ni in neighbors_indices:
            edges[i].append(ni)
            edges[ni].append(i)  # For undirected graph

    # create a mapping from state tuple to index to avoid errors
    state_to_index = {tuple(v): i for i, v in enumerate(vertices)}

    # create a robot planning problem for A* search
    problem = RobotPlanningProblem(vertices, edges, tuple(start_config), tuple(goal_config), state_to_index, link_lengths)

    return astar_search(problem, problem.heuristic_fn)
