"""Finite automaton"""
import numpy as np
from random import randint
from math import sqrt
from grid import Grid
from variables import Variables
from entity import *


class CellCounter:

    def __init__(self):
        self.immune_cell = 0
        self.tumor_cell = 0
        self.proliferating_cell = 0

class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid: Grid, variables: Variables) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid
        self.variables = variables
        self.edge_cells = []

    def next(self) -> None:
        """Make step in automaton"""

        cells = self.grid.cells.copy()
        random_variables = np.random.rand(len(cells), 3)
        counter = CellCounter()

        if self.edge_cells:
            self.variables.Rt = sum(cell.distance for cell in self.edge_cells) \
                // len(self.edge_cells)

        edge_cells = []

        for cell in edge_cells:
            cell.entity.energy_level = self.variables.max_energy_level

        for i, cell in enumerate(cells):
            if cell.empty:
                continue

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = cell.neighbors
            entity.free_neighbors = cell.get_free_neighbor()

            max_energy_neighbor = max(entity.neighbors, key=lambda c: c.entity.energy_level
                                      if c.entity else float('inf'))

            if max_energy_neighbor.entity:
                entity.energy_level = max_energy_neighbor.entity.energy_level - 1
            else:
                entity.energy_level = self.variables.max_energy_level

            if entity.free_neighbors:
                edge_cells.append(cell)

            counter.immune_cell += 1 if isinstance(entity, ImmuneCell) else 0
            counter.tumor_cell += 1 if isinstance(entity, CancerCell) else 0

            entity.next_state(self.variables, *random_variables[i])

            entity.cell = None
            entity.neighbors = None
            entity.free_neighbors = None

        self.edge_cells = edge_cells

        self.spawn_immune_cells(counter)

    def spawn_immune_cells(self, counter: CellCounter):
        recrutient = 2 * counter.immune_cell * counter.tumor_cell / (10 ** 3 + counter.tumor_cell)

        if counter.immune_cell >= 1000:
            return

        for _ in range(int(recrutient)):
            free_cell = self.grid.get_random_free_cell()
            free_cell.entity = ImmuneCell()
