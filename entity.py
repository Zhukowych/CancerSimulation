"""Entities"""
import math
import numpy as np
from variables import Variables
from random import random, choice
from cell import Cell


class Entity:
    """Entity"""

    __dict__ = ["cell", "neighbors", "free_neighbors"]

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



MAX_PROLIFERATION_POTENTIAL = 30
MAX_PROLIFERATION_COLOR = np.array([250,0,0])
LOW_PROLIFERATION_COLOR = np.array([0, 0, 0])

DELTA = ( MAX_PROLIFERATION_COLOR - LOW_PROLIFERATION_COLOR ) / MAX_PROLIFERATION_POTENTIAL
print(DELTA)


def get_chemo_death_probability(theta, k, y, variables: Variables) -> float:
    """Return probability of cell's death due to chemotherapy"""
    l = k * variables.drug_concentration / (theta * y * variables.injection_number + 1)
    return l * variables.PK * math.e ** ( -variables.ci * (variables.days_elapsed - \
            variables.injection_number * variables.time_constant))


class BiologicalCell(Entity):
    """Biological cell"""

    ID = 1

    __dict__ = ["ID", "proliferation_potential", "cell", "neighbors", "free_neighbors"]

    def __init__(self, proliferation_potential=MAX_PROLIFERATION_POTENTIAL, *args, **kwargs) -> None:
        """Initialize Biological cell"""
        super().__init__(*args, **kwargs)

        self.proliferation_potential = proliferation_potential
        self.energy_level = 0

    @property
    def apotisis_probability(self) -> float:
        """Return probability of spontaneous death"""
        return 0

    @property
    def proliferation_probability(self) -> float:
        """Return probability of proliferation"""
        return 0.047

    @property
    def migration_probability(self) -> float:
        """Return probability of migration"""
        return 0.8

    def next_state(self, *random_values) -> None:
        """Next state implementation to BiologicalCell"""
        pass

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

    def __init__(self, proliferation_potential=MAX_PROLIFERATION_POTENTIAL,
                 *args, **kwargs) -> None:
        super().__init__(proliferation_potential, *args, **kwargs)

    def next_state(self, variables: Variables, *random_variables) -> None:
        apotosis, proliferation, migration, theta, death = random_variables

        br = variables.p0 * (1 - (self.cell.distance / (variables.Rmax - variables.Kc) ))

        if apotosis <= self.apotisis_probability:
            self.apotose()
            return

        if proliferation <= br:
            self.proliferate()

        if migration <= self.migration_probability:
            self.move_to_random()

        self.process_chemotherapy(variables=variables, theta=theta, death=death)

        if self.energy_level <= variables.necrotic_energy_level:
            self.cell.entity = NecroticCell()


    def process_chemotherapy(self, variables: Variables, theta: float, death: float) -> None:
        """Process the effect of the chemotherapy"""

        if not variables.is_treatment:
            return

        chemo_death_probability = self.get_chemo_death_probability(theta=theta, variables=variables)

        if death <= chemo_death_probability:
            self.apotose()


    def get_chemo_death_probability(self, variables, theta) -> float:
        """Return the probability of death due to chemotherapy"""
        return get_chemo_death_probability(theta=theta,
                                           k=variables.kPC,
                                           y=variables.yPC,
                                           variables=variables)

    def replicate(self) -> Entity:
        """Return daughter cell"""
        daughter =  CancerCell(self.proliferation_potential - 1)
        self.proliferation_potential -= 1
        return daughter

    @property
    def color(self) -> tuple[int, int, int]:
        r, g, b =  LOW_PROLIFERATION_COLOR + self.proliferation_potential * DELTA
        return int(r), int(g), int(b)


class QuiescentCell(BiologicalCell):
    """Quiescent cell"""

    def next_state(self, variables: Variables, *random_variables) -> None:
        
        if self.distance_from_edge < variables.Wp or self.free_neighbors:
            self.cell.entity = CancerCell()

        if self.cell.distance < variables.Rn:
            self.cell.entity = NecroticCell()

    @property
    def color(self):
        return (219, 134, 134)


class NecroticCell(BiologicalCell):
    """Necrotic cell"""

    def next_state(self, variables: Variables, *random_variables) -> None:
        pass

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
        if new_stem_chance <= 0.4:
            daughter = TrueStemCell(self.proliferation_potential)
        else:
            daughter =  CancerCell(self.proliferation_potential)
        return daughter

    def get_chemo_death_probability(self, variables, theta) -> float:
        return 0

    @property
    def color(self):
        return 255, 238, 0


class ImmuneCell(BiologicalCell):
    """Immune cell"""

    def next_state(self, variables: Variables, *random_values) -> None:
        *_, cancer_cell_death_probability, immune_cell_death_probability = random_values

        self.move_to_random(immune_cell_death_probability)

        for neighbor in self.neighbors:
            if neighbor.empty:
                continue

            if isinstance(neighbor.entity, CancerCell):
                if cancer_cell_death_probability <= variables.pdT:
                    neighbor.entity = None

                if immune_cell_death_probability <= variables.pdI:
                    self.apotose()

                break

    def move_to_random(self, direction_probability) -> None:
        """Move to random free neighbor"""

        if direction_probability <= 0.2:
            free_neighbor = sorted(self.free_neighbors, key=lambda c: c.distance)[:3]
        else:
            free_neighbor = sorted(self.free_neighbors, key=lambda c: c.distance)

        if not self.cell.entity: # cell has died
            return

        if not free_neighbor:
            return

        cell = choice(free_neighbor)
        self.move_to(cell)

    @property
    def color(self):
        return 245, 91, 209
