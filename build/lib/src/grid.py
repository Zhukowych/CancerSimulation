"""Grid and cell"""

from typing import Iterable
import numpy as np
from random import randint
from math import sqrt
from .cell import Cell
from .entity import Entity


class Grid:
    """Grid"""

    def __init__(self, width=1000, height=1000) -> None:
        """Initialize the grid"""

        self.width = width
        self.height = height

        self.active_cells = set()
        self.grid = [[Cell(x, y) for x in range(width)] for y in range(height)]

        for row in self.grid:
            for cell in row:
                cx, cy = self.center
                cell.add_entity_callback = lambda c: self.add_active_cell(c)
                cell.remove_entity_callback = lambda c: self.remove_active_cell(c)
                cell.neighbors = self.get_neighbors_of(cell)
                cell.distance = sqrt((cell.x - cx) ** 2 + (cell.y - cy) ** 2)
                cell.phi = np.arctan2(cell.y - cy, cell.x - cx)

    @property
    def center(self) -> tuple[int, int]:
        """Return coordinate of center"""
        return (self.width // 2, self.height // 2)

    @property
    def cells(self) -> Iterable:
        """Return all cells iterator"""
        return self.active_cells

    @property
    def coloured_cells(self) -> Iterable:
        return [(cell.x, cell.y, cell.entity.color) for cell in self.active_cells]

    def add_active_cell(self, cell: Cell) -> None:
        """Add active cell"""
        self.active_cells.add(cell)

    def remove_active_cell(self, cell: Cell) -> None:
        """Add active cell"""
        self.active_cells.remove(cell)

    def place_entity(self, entity: Entity, x: int, y: int) -> None:
        """Place entity on grid by coordinates"""
        if not -self.width < x < self.width or not -self.height < y < self.height:
            raise ValueError("You cannot put an entity outside the boundaries")

        self.grid[y][x].entity = entity
        self.add_active_cell(self.grid[y][x])

    def to_array(self) -> list[list[int]]:
        """
        Convert list of Cell objects to list of int
        """
        return [[cell.entity_id for cell in row] for row in self.grid]

    def get_neighbors_of(self, cell: Cell) -> list[Cell]:
        """
        Return neighbors of given cell - all adjacent cells
        in the grid
        """

        neighbors = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == dy == 0:
                    continue

                x = (cell.x + dx) % self.width
                y = (cell.y + dy) % self.height

                neighbors.append(self.grid[y][x])

        return neighbors

    def get_random_free_cell(self) -> Cell:
        """Return random free cell"""
        x, y = randint(0, self.width - 1), randint(0, self.height - 1)
        while not self.grid[x][y].empty:
            x, y = randint(0, self.width - 1), randint(0, self.height - 1)
        return self.grid[x][y]
