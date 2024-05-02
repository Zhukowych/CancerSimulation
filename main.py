import time
import seaborn as sns
import matplotlib.pyplot as plt

from grid import Grid
from automaton import FiniteAutomaton
from entity import BiologicalCell

if __name__ == "__main__":
    cell = BiologicalCell()

    grid = Grid(1000, 1000)
    automaton = FiniteAutomaton(grid)

    plt.ion()
    plt.figure()
    plt.show()

    grid.place_entity(cell, 20, 20)

    for i in range(20, 10000):

        if i % 100 == 0:
            print(f"Iteration: {i=}")

        start = time.perf_counter()
        data = grid.to_array()
        plt.clf()
        automaton.next()
        print(f"Iteration time:", time.perf_counter() - start)
        
        sns.heatmap(data=data, square=True, cbar=False, cbar_kws={"drawedges": True})
        plt.pause(10e-100)
