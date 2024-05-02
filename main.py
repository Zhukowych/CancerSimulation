import seaborn as sns
import matplotlib.pyplot as plt

from grid import Grid
from automaton import FiniteAutomaton
from entity import BiologicalCell

if __name__ == "__main__":
    cell = BiologicalCell()

    grid = Grid(100, 100)
    automaton = FiniteAutomaton(grid)

    plt.ion()
    plt.figure()
    plt.show()

    grid.place_entity(cell, 20, 20)

    for i in range(20, 50):
        data = grid.to_array()
        plt.clf()
        sns.heatmap(data=data, square=True, cbar=False, cbar_kws={"drawedges": True})
        automaton.next()
        plt.pause(10e-10)

        
