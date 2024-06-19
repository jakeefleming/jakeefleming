from display import display_sudoku_solution
import random, sys, timeit
from SAT import SAT

if __name__ == "__main__":
    # for testing, always initialize the pseudorandom number generator to output the same sequence
    #  of values:
    # seed I found that solves puzzle one very quickly
    random.seed(3170813971201277318)

    puzzle_name = "puzzle1"
    # puzzle_name = str(sys.argv[1][:-4])
    sol_filename = puzzle_name + ".sol"

    sat = SAT(puzzle_name + ".cnf")
    # sat = SAT(sys.argv[1])

    start = timeit.default_timer()
    result = sat.walk_sat(0.7, 100000)
    # result = sat.simulated_annealing(1000, 0.995, 1e-100)
    end = timeit.default_timer()

    print(end - start)

    if result:
        sat.write_solution(sol_filename)
        display_sudoku_solution(sol_filename)