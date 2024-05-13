"""Finite automaton"""

import numpy as np
from random import randint
from math import sqrt
from .grid import Grid
from .variables import Variables
from .entity import *


class CellCounter:

    def __init__(self):
        self.immune_cell = 0
        self.tumor_cell = 0
        self.proliferating_cell = 0
        self.stem_cell = 0


class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid: Grid, variables: Variables) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid
        self.variables = variables
        self.edge_cells = []
        self.counter = None

    def next(self) -> None:
        """Make step in automaton"""

        cells = self.grid.cells.copy()
        random_variables = np.random.rand(len(cells), 5)
        self.counter = CellCounter()

        if self.edge_cells:
            self.variables.Rt = sum(cell.distance for cell in self.edge_cells) // len(
                self.edge_cells
            )

        edge_cells = []

        for cell in edge_cells:
            cell.entity.energy_level = 0

        for i, cell in enumerate(cells):
            if cell.empty:
                continue

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = cell.neighbors
            entity.free_neighbors = cell.get_free_neighbor()
            entity.variables = self.variables

            min_energy_neighbor = min(
                entity.neighbors,
                key=lambda c: c.entity.energy_level if c.entity else 0,
            )

            if min_energy_neighbor.entity:
                entity.energy_level = min_energy_neighbor.entity.energy_level + 1
            else:
                entity.energy_level = 0

            if entity.free_neighbors:
                edge_cells.append(cell)

            self.counter.immune_cell += 1 if isinstance(entity, ImmuneCell) else 0
            self.counter.tumor_cell += 1 if isinstance(entity, CancerCell) else 0
            self.counter.stem_cell += 1 if isinstance(entity, TrueStemCell) else 0

            entity.next_state(self.variables, *random_variables[i])

            entity.cell = None
            entity.neighbors = None
            entity.free_neighbors = None

        self.edge_cells = edge_cells

        self.process_chemotherapy()
        self.spawn_immune_cells()

    def process_chemotherapy(self):
        """Process effect of chemotherapy on cell"""
        if self.variables.is_injection_start:
            self.variables.injection_number += 1

    def spawn_immune_cells(self):
        """Spawn immune cells on the grid"""
        recrutient = (
            2 * self.counter.immune_cell * self.counter.tumor_cell / (10**3 + self.counter.tumor_cell)
        )
        if self.counter.immune_cell >= self.variables.max_immune_cell_count:
            return

        for _ in range(int(recrutient)):
            free_cell = self.grid.get_random_free_cell()
            free_cell.entity = ImmuneCell()
