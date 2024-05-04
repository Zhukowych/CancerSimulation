import time

from grid import Grid
from automaton import FiniteAutomaton
from entity import ClonogenicStemCell, BiologicalCell
from line_profiler import profile

@profile
def main():
    cell = BiologicalCell()

    grid = Grid(500, 500)
    automaton = FiniteAutomaton(grid)


    grid.place_entity(cell, 50, 50)


    for i in range(20, 1000):

        if i % 100 == 0:
            print(f"Iteration: {i=}", "cell count", len(grid.cells))

        automaton.next()




if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"Total time {time.perf_counter() - start}")
