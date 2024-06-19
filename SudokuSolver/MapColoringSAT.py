# Jake Fleming

from SAT import SAT
import random


def generate_map_coloring_constraints(neighbors, filename):
    with open(filename, 'w') as file:
        # clauses that say each region has at least one color
        for region in neighbors:
            for color in range(1, 5):  # we use four coloring theorem
                file.write(f"{region}_{color} ")
            file.write("\n")

        # clauses that say each region has at most one color
        for region in neighbors:
            for color1 in range(1, 5):
                for color2 in range(color1 + 1, 5):
                    file.write(f"-{region}_{color1} -{region}_{color2}\n")

        # clauses that form constraints where neighbors cannot share a color
        for region, region_neighbors in neighbors.items():
            for neighbor in region_neighbors:
                for color in range(1, 5):
                    file.write(f"-{region}_{color} -{neighbor}_{color}\n")


# map of USA!
neighbors = {
    "AL": ["MS", "TN", "GA", "FL"],
    "AK": [],
    "AZ": ["CA", "NV", "UT", "CO", "NM"],
    "AR": ["MO", "TN", "MS", "LA", "TX", "OK"],
    "CA": ["OR", "NV", "AZ"],
    "CO": ["WY", "UT", "AZ", "NM", "OK", "KS", "NE"],
    "CT": ["NY", "MA", "RI"],
    "DE": ["MD", "PA", "NJ"],
    "FL": ["GA", "AL"],
    "GA": ["FL", "AL", "TN", "NC", "SC"],
    "HI": [],
    "ID": ["MT", "WY", "UT", "NV", "OR", "WA"],
    "IL": ["IN", "KY", "MO", "IA", "WI"],
    "IN": ["MI", "OH", "KY", "IL"],
    "IA": ["MN", "WI", "IL", "MO", "NE", "SD"],
    "KS": ["NE", "MO", "OK", "CO"],
    "KY": ["IN", "OH", "WV", "VA", "TN", "MO", "IL"],
    "LA": ["TX", "AR", "MS"],
    "ME": ["NH"],
    "MD": ["PA", "DE", "VA", "WV"],
    "MA": ["RI", "CT", "NY", "NH", "VT"],
    "MI": ["IN", "OH", "WI"],
    "MN": ["ND", "SD", "IA", "WI"],
    "MS": ["TN", "AL", "LA", "AR"],
    "MO": ["IA", "IL", "KY", "TN", "AR", "OK", "KS", "NE"],
    "MT": ["ID", "WY", "SD", "ND"],
    "NE": ["SD", "IA", "MO", "KS", "CO", "WY"],
    "NV": ["OR", "CA", "AZ", "UT", "ID"],
    "NH": ["VT", "ME", "MA"],
    "NJ": ["DE", "PA", "NY"],
    "NM": ["AZ", "UT", "CO", "OK", "TX"],
    "NY": ["NJ", "PA", "VT", "MA", "CT"],
    "NC": ["GA", "SC", "TN", "VA"],
    "ND": ["MT", "SD", "MN"],
    "OH": ["MI", "IN", "KY", "WV", "PA"],
    "OK": ["KS", "MO", "AR", "TX", "NM", "CO"],
    "OR": ["WA", "ID", "NV", "CA"],
    "PA": ["NY", "NJ", "DE", "MD", "WV", "OH"],
    "RI": ["MA", "CT"],
    "SC": ["GA", "NC"],
    "SD": ["ND", "MT", "WY", "NE", "IA", "MN"],
    "TN": ["KY", "VA", "NC", "GA", "AL", "MS", "AR", "MO"],
    "TX": ["OK", "AR", "LA", "NM"],
    "UT": ["ID", "WY", "CO", "NM", "AZ", "NV"],
    "VT": ["NY", "NH", "MA"],
    "VA": ["NC", "TN", "KY", "WV", "MD"],
    "WA": ["ID", "OR"],
    "WV": ["OH", "PA", "MD", "VA", "KY"],
    "WI": ["MN", "IA", "IL", "MI"],
    "WY": ["MT", "SD", "NE", "CO", "UT", "ID"]
}

random.seed(1)
generate_map_coloring_constraints(neighbors, "map_coloring.cnf")
sat_cm = SAT("map_coloring.cnf")
sat_cm.walk_sat(0.7, 100000)
sat_cm.write_solution("map_coloring.sol")

# print the solution using the .sol file SAT writes
file = open("map_coloring.sol", "r")
for line in file:
    line.strip()
    # for all of our true values, find the color at the end of the variable
    if line[0] != "-":
        color = line[-2]
        if color == "1":
            color = "red"
        elif color == "2":
            color = "blue"
        elif color == "3":
            color = "green"
        else:
            color = "yellow"
        # get the state string by reducing it to just letters
        state = ""
        for char in line:
            if char.isalpha():
                state += char
        print(state, color)
file.close()
