"""Entities"""
import random
from cell import Cell


class Entity:
    """Entity"""

    def __init__(self) -> None:
        """Initialize entity"""
        self.cell = None
        self.neighbors = None

    def next_state(self) -> None:
        """Mutate cell or neighbors to represent the next state"""

    def move_to(self, next_cell: Cell) -> None:
        """Move from current cell to next"""
        self.cell.entity = None
        next_cell.entity = self

    def move_to_random(self) -> None:
        """Move to random free neighbor"""
        free_neighbor = self.get_free_neighbor()
        if not free_neighbor:
            return

        cell = random.choice(free_neighbor)
        self.move_to(cell)

    def get_free_neighbor(self) -> Cell:
        """Return empty cell"""
        return [cell for cell in self.neighbors if cell.empty]


class BiologicalCell(Entity):
    """Biological cell"""
    ID = 1

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return 0

    @property
    def proliferation_probability(self) -> float:
        """Return probability of proliferation"""
        return 0

    @property
    def migration_probability(self) -> float:
        """Return probability of migration"""
        return 1

    def next_state(self) -> None:
        """Next state implementation to BiologicalCell"""
        self.move_to_random()


class Tumor
