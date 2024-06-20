# Author: Jake Fleming

import matplotlib.pyplot as plt
import math
from shapely.geometry import Polygon, Point
from PRM import prm_planner, compute_end_points, draw_robot_arm, show_plot

# two angles
space_bounds = [(0, 2 * math.pi), (0, 2 * math.pi)]

# two lines
link_lengths = [1, 1]

# two circles and a rectangle
obstacle1 = Point(-0.5, -0.5).buffer(0.25)
obstacle2 = Polygon([(1.5, 0), (1.5, 2), (2, 2), (2, 0)])
obstacle3 = Point(0, 1).buffer(0.5)

obstacles = [obstacle1, obstacle2, obstacle3]

# start and goal
start_config = [math.pi / 4, math.pi / 4]
goal_config = [3 * math.pi / 2, math.pi / 2]

# 2000 vertices, each with out-degree 6
num_samples = 2000
k = 6

# find the path
path = prm_planner(start_config, goal_config, obstacles, space_bounds, link_lengths, num_samples, k).path

# draw each configuration - same coloring as before
for config in range(len(path)):
    points = compute_end_points(path[config], link_lengths)
    if config == 0:
        draw_robot_arm(points, 'bo-')
    elif config == len(path) - 1:
        draw_robot_arm(points, 'go-')
    else:
        draw_robot_arm(points, 'ro-')

# draw each obstacle
for obstacle in obstacles:
    x, y = obstacle.exterior.xy
    plt.fill(x, y, alpha=0.5, fc='r', ec='none')

# plot everything
show_plot()
