"""Entities"""
import numpy as np
from random import random, choice
from cell import Cell


class Entity:
    """Entity"""

    __dict__ = [
        "cell",
        "neighbors",
        'free_neighbors'
    ]

    def __init__(self) -> None:
        """Initialize entity"""
        self.cell = None
        self.neighbors = None
        self.free_neighbors = None

    def next_state(self) -> None:
        """Mutate cell or neighbors to represent the next state"""

    def move_to(self, next_cell: Cell) -> None:
        """Move from current cell to next"""
        self.cell.entity = None
        next_cell.entity = self

    def move_to_random(self) -> None:
        """Move to random free neighbor"""
        free_neighbor = self.free_neighbors

        if not self.cell.entity: # cell has died
            return 

        if not free_neighbor:
            return

        cell = choice(free_neighbor)
        self.move_to(cell)



MAX_PROLIFERATION_POTENTIAL = 20
MAX_PROLIFERATION_COLOR = np.array([250,0,0])
LOW_PROLIFERATION_COLOR = np.array([0, 0, 0])

DELTA = ( MAX_PROLIFERATION_COLOR - LOW_PROLIFERATION_COLOR ) / MAX_PROLIFERATION_POTENTIAL
print(DELTA)

class BiologicalCell(Entity):
    """Biological cell"""

    ID = 1

    __dict__ = [
        "ID",
        "proliferation_potential",
        "cell",
        "neighbors",
        "free_neighbors"
    ]

    def __init__(self, proliferation_potential=MAX_PROLIFERATION_POTENTIAL, *args, **kwargs) -> None:
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
        return 0.4

    def next_state(self, *random_values) -> None:
        """Next state implementation to BiologicalCell"""
        apotisis, proliferation, migration = random_values

        if apotisis <= self.apotisis_probability or self.proliferation_potential == 0:
            self.apotose()
            return

        if proliferation <= self.proliferation_probability:
            self.proliferate()

        if migration <= self.migration_probability:
            self.move_to_random()

    def proliferate(self) -> None:
        """Proliferate"""
        free_neighbors = self.free_neighbors
        if not free_neighbors:
            return

        free_cell = choice(free_neighbors)

        if self.proliferation_potential <= 0:
            self.apotose()
            return

        free_cell.entity = self.replicate()

    def replicate(self) -> Entity:
        """Return daughter cell"""
        daughter =  BiologicalCell(self.proliferation_potential - 1)
        self.proliferation_potential -= 1
        return daughter

    def apotose(self) -> None:
        """Cell death"""
        self.cell.entity = None

    @property
    def color(self):
        r, g, b =  LOW_PROLIFERATION_COLOR + self.proliferation_potential * DELTA
        return int(r), int(g), int(b)



class CancerCell(BiologicalCell):
    """Cancer cell"""

    def next_state(self, *random_values) -> None:
        apotisis, proliferation, migration = random_values

        if apotisis <= self.apotisis_probability or self.proliferation_potential == 0:
            self.apotose()
            return

        if proliferation <= self.proliferation_probability:
            self.proliferate()

        if migration <= self.migration_probability:
            self.move_to_random()
        



class RTCCell(CancerCell):
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


class TrueStemCell(CancerCell):
    """
    True Stem cell.
    Cell that is immortal and can give birth to either
    RTC or other True stem cell
    """
    ID = 3

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return 0

    def replicate(self) -> Entity:
        """Return daughter cell"""
        new_stem_chance = random()
        if new_stem_chance <= 0.3:
            daughter = TrueStemCell(self.proliferation_potential)
        else:
            daughter =  RTCCell(self.proliferation_potential - 1)
        return daughter

    @property
    def color(self):
        return 255, 238, 0
