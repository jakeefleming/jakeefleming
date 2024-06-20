# Author: Jake Fleming

import matplotlib.pyplot as plt
import math
from shapely.geometry import Polygon
from PRM import prm_planner, compute_end_points, draw_robot_arm, show_plot

# three angles
space_bounds = [(0, 2 * math.pi), (0, 2 * math.pi), (0, 2 * math.pi)]

# the lines
link_lengths = [1, 1, 1]

# rectangle and square obstacles
obstacle1 = Polygon([(-1, 0.5), (-1, 1.5), (0, 1.5), (0, 0.5)])
obstacle2 = Polygon([(2, 0), (2, 2), (3, 2), (3, 0)])

obstacles = [obstacle1, obstacle2]

# start and goal
start_config = [math.pi / 4, math.pi / 4, math.pi / 4]
goal_config = [math.pi, 0, 0]

# 1000 vertices, out-degree 4 for each vertex
num_samples = 1000
k = 4

# create the path
path = prm_planner(start_config, goal_config, obstacles, space_bounds, link_lengths, num_samples, k).path

# draw all the configurations - make the start blue, end green, and transitions red
for config in range(len(path)):
    points = compute_end_points(path[config], link_lengths)
    if config == 0:
        draw_robot_arm(points, 'bo-')
    elif config == len(path) - 1:
        draw_robot_arm(points, 'go-')
    else:
        draw_robot_arm(points, 'ro-')

# draw all the obstacles
for obstacle in obstacles:
    x, y = obstacle.exterior.xy
    plt.fill(x, y, alpha=0.5, fc='r', ec='none')

# graph everything
show_plot()
