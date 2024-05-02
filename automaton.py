"""Finite automaton"""
from grid import Grid


class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid: Grid) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid

    def next(self) -> None:
        """Make step in automaton"""

        for cell in self.grid.cells:

            if cell.empty:
                continue

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = self.grid.get_neighbors_of(cell)

            entity.next_state()

            entity.cell = None
            entity.neighbors = None
