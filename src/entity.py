"""Entities"""
import math
import numpy as np
from random import random, choice
from .variables import Variables, LOW_PROLIFERATION_COLOR, MAX_PROLIFERATION_COLOR
from .cell import Cell



def get_chemo_death_probability(theta, k, y, variables: Variables) -> float:
    """Return probability of cell's death due to chemotherapy"""
    l = k * variables.drug_concentration / (theta * y * variables.injection_number + 1)
    return l * variables.PK * math.e ** ( -variables.ci * variables.days_from_injection)


class Entity:
    """Entity"""

    __dict__ = ["cell", "neighbors", "free_neighbors", "variables"]

    def __init__(self) -> None:
        """Initialize entity"""
        self.cell = None
        self.neighbors = None
        self.free_neighbors = None
        self.variables = None

    def next_state(self, *args, **kwargs) -> None:
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


class BiologicalCell(Entity):
    """Biological cell"""

    ID = 1

    __dict__ = ["ID", "proliferation_potential", "cell", "neighbors", "free_neighbors", "variables"]

    def __init__(self, *args, proliferation_potential=None, **kwargs) -> None:
        """Initialize Biological cell"""
        super().__init__(*args, **kwargs)

        self.proliferation_potential = proliferation_potential
        self.energy_level = 0

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return self.variables.pA

    @property
    def proliferation_probability(self) -> float:
        """Return probability of proliferation"""
        return self.variables.p0 * (1 - (self.cell.distance / (self.variables.Rmax - self.variables.Kc) ))

    def process_chemotherapy(self, theta: float, death: float) -> None:
        """Process the effect of the chemotherapy"""
        if not self.variables.is_treatment:
            return

        chemo_death_probability = self.get_chemo_death_probability(theta=theta)
        if death <= chemo_death_probability:
            self.apotose()

    def get_chemo_death_probability(self, theta) -> float:
        """Return the probability of death due to chemotherapy"""
        return 0

    @property
    def migration_probability(self) -> float:
        """Return probability of migration"""
        return self.variables.mu

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
        daughter =  BiologicalCell(proliferation_potential=self.proliferation_potential - 1)
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

    def next_state(self, *random_variables) -> None:
        apotosis, proliferation, migration, theta, death, *_ = random_variables

        if apotosis <= self.apotisis_probability:
            self.apotose()
            return

        if proliferation <= self.proliferation_probability:
            self.proliferate()

        if migration <= self.migration_probability:
            self.move_to_random()

        self.process_chemotherapy(theta=theta, death=death)

        if self.energy_level >= self.variables.quiescent_distance:
            self.cell.entity = QuiescentCell(self)

        if self.energy_level >= self.variables.necrotic_distance:
            self.cell.entity = NecroticCell()


    def get_chemo_death_probability(self, theta) -> float:
        """Return the probability of death due to chemotherapy"""
        return  get_chemo_death_probability(theta=theta,
                                             k=self.variables.kPC,
                                             y=self.variables.yPC,
                                             variables=self.variables)

    def replicate(self) -> Entity:
        """Return daughter cell"""
        daughter =  CancerCell(proliferation_potential=self.proliferation_potential - 1)
        self.proliferation_potential -= 1
        return daughter

    @property
    def color(self) -> tuple[int, int, int]:
        if not self.variables:
            r, g, b = MAX_PROLIFERATION_COLOR
        else:
            r, g, b =  LOW_PROLIFERATION_COLOR + self.proliferation_potential * self.variables.color_delta
        return int(r), int(g), int(b)


class QuiescentCell(CancerCell):
    """Quiescent cell"""

    def __init__(self, previous_entity, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_entity = previous_entity

    def next_state(self, *_) -> None:
        if self.energy_level < self.variables.quiescent_distance:
            self.cell.entity = self.previous_entity

        if self.energy_level > self.variables.necrotic_distance:
            self.cell.entity = NecroticCell()

    @property
    def color(self):
        return self.previous_entity


class NecroticCell(CancerCell):
    """Necrotic cell"""

    def next_state(self, *args, **kwargs) -> None:
        """Necrotic cell cannot do anything"""

    @property
    def color(self):
        return (133, 21, 21)


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
        if new_stem_chance <= self.variables.pS:
            daughter = TrueStemCell(proliferation_potential=self.proliferation_potential)
        else:
            daughter =  CancerCell(proliferation_potential=self.proliferation_potential)
        return daughter

    def get_chemo_death_probability(self, theta) -> float:
        return 0

    @property
    def color(self):
        return 255, 238, 0


class ImmuneCell(BiologicalCell):
    """Immune cell"""

    def next_state(self, *random_values) -> None:
        *_, theta , death, cancer_cell_death_probability, immune_cell_death_probability = random_values

        self.move_to_random(immune_cell_death_probability)

        for neighbor in self.neighbors:
            if neighbor.empty:
                continue

            if isinstance(neighbor.entity, CancerCell):
                if cancer_cell_death_probability <= self.variables.pdT:
                    neighbor.entity = None

                if immune_cell_death_probability <= self.variables.pdI:
                    self.apotose()

                break

        self.process_chemotherapy(death=death, theta=theta)


    def get_chemo_death_probability(self, theta) -> float:
        """Return the probability of death due to chemotherapy"""
        return  get_chemo_death_probability(theta=theta,
                                             k=self.variables.kI,
                                             y=self.variables.yI,
                                             variables=self.variables)

    def move_to_random(self, direction_probability) -> None:
        """Move to random free neighbor"""

        if not self.cell.entity: # cell has died
            return

        if not self.free_neighbors:
            return

        cell = choice(self.free_neighbors)
        self.move_to(cell)   

    @property
    def color(self):
        return 245, 91, 209
