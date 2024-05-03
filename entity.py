"""Entities"""

from random import random, choice
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

        cell = choice(free_neighbor)
        self.move_to(cell)

    def get_free_neighbor(self) -> Cell:
        """Return empty cell"""
        return [cell for cell in self.neighbors if cell.empty]


class BiologicalCell(Entity):
    """Biological cell"""

    ID = 1

    def __init__(self, proliferation_potential=10, *args, **kwargs) -> None:
        """Initialize Biological cell"""
        super().__init__(*args, **kwargs)

        self.proliferation_potential = proliferation_potential

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return 0.001

    @property
    def proliferation_probability(self) -> float:
        """Return probability of proliferation"""
        return 0.047

    @property
    def migration_probability(self) -> float:
        """Return probability of migration"""
        return 0.1

    def next_state(self, *random_values) -> None:
        """Next state implementation to BiologicalCell"""
        apotisis, proliferation, migration = random_values

        if apotisis <= self.apotisis_probability:
            self.apotose()
            return

        if proliferation <= self.proliferation_probability:
            self.proliferate()

        if migration <= self.migration_probability:
            self.move_to_random()

    def proliferate(self) -> None:
        """Proliferate"""
        free_neighbors = self.get_free_neighbor()

        if not free_neighbors:
            return

        free_cell = choice(free_neighbors)

        if not self.proliferation_potential:
            self.apotose()
            return


        free_cell.entity = self.replicate()

    def replicate(self) -> Entity:
        """Return daughter cell"""
        self.proliferation_potential -= 1
        return BiologicalCell(self.proliferation_potential - 1)

    def apotose(self) -> None:
        """Cell death"""
        self.cell.entity = None

    @property
    def color(self) -> tuple[int, int, int]:
        return (255, 255, 255)


class RTCCell(BiologicalCell):
    """
    Regular tumor cell
    """

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return 0.001

    @property
    def proliferation_probability(self) -> float:
        """Return probability of proliferation"""
        return 0.041

    @property
    def migration_probability(self) -> float:
        """Return probability of migration"""
        return 0.12

    def replicate(self) -> Entity:
        """Return daughter cell"""
        self.proliferation_potential -= 1
        return RTCCell(self.proliferation_potential - 1)

    @property
    def color(self):
        return (255, 0, 0)


class ClonogenicStemCell(BiologicalCell):
    """
    Clonogenic stem cell.
    Stem cell that is immortal, but can not give
    birth to other stem cells
    """
    ID = 2

    def replicate(self) -> Entity:
        """Return daughter cell"""
        return RTCCell(self.proliferation_potential - 1)

class TrueStemCell(BiologicalCell):
    """
    True Stem cell.
    Cell that is immortal and can give birth to either
    RTC or other True stem cell
    """
    ID = 3

    def replicate(self) -> Entity:
        """Return daughter cell"""
        return TrueStemCell(self.proliferation_potential)
