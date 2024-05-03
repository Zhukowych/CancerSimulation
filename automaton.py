"""Finite automaton"""
import numpy as np
from grid import Grid
from line_profiler import profile

class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid: Grid) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid

    @profile
    def next(self) -> None:
        """Make step in automaton"""

        cells = self.grid.cells[:]

        random_variables = np.random.rand(len(cells), 3)

        for i, cell in enumerate(cells):
            if cell.empty:
                continue

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = cell.neighbors

            entity.next_state(*random_variables[i])

            entity.cell = None
            entity.neighbors = None
