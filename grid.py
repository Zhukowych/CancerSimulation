"""Grid and cell"""
from typing import Iterable
from cell import Cell
from entity import Entity


class Grid:
    """Grid"""    

    def __init__(self, width=1000, height=1000) -> None:
        """Initialize the grid"""        

        self.width = width
        self.height = height

        self.filled_cells = []
        self.grid = [ [Cell(x, y) for x in range(width)]
                       for y in range(height) ]

    @property
    def cells(self) -> Iterable:
        """Return all cells iterator"""
        return iter(cell for row in self.grid
                         for cell in row)

    def place_entity(self, entity: Entity, x: int, y: int) -> None:
        """Place entity on grid by coordinates"""
        if not -self.width < x < self.width or not -self.height < y < self.height:
            raise ValueError("You cannot put an entity outside the boundaries")

        self.grid[y][x].entity = entity

    def to_array(self) -> list[list[int]]:
        """
        Convert list of Cell objects to list of int
        """
        return [ [ cell.entity_id for cell in row] for row in self.grid ]

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
