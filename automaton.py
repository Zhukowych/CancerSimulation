"""Finite automaton"""
import numba
import threading
import numpy as np
from grid import Grid

from concurrent.futures import ThreadPoolExecutor


class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid: Grid) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid

    def next(self) -> None:
        """Make step in automaton"""

        cells = self.grid.cells.copy()

        random_variables = np.random.rand(len(cells), 3)

        for i, cell in enumerate(cells):

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = cell.neighbors
            entity.free_neighbors = cell.get_free_neighbor()

            entity.next_state(*random_variables[i])

            entity.cell = None
            entity.neighbors = None
            entity.free_neighbors = None
