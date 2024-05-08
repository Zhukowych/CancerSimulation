"""Finite automaton"""

import numba
import threading
import numpy as np

from concurrent.futures import ThreadPoolExecutor


class FiniteAutomaton:
    """Finite automaton"""

    def __init__(self, grid) -> None:
        """Initialize FiniteAutomaton"""
        self.grid = grid

    def next(self) -> None:
        """Make step in automaton"""

        cells = self.grid.cells.copy()

        random_variables = np.random.rand(len(cells), 3)

        for i, cell in enumerate(cells):

            entity = cell.entity

            entity.cell = cell
            entity.neighbors = cell.neighbors
            entity.free_neighbors = cell.get_free_neighbor()

            entity.next_state(*random_variables[i])

            entity.cell = None
            entity.neighbors = None
            entity.free_neighbors = None


"""Grid and cell"""
from typing import Iterable


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
                cell.add_entity_callback = lambda c: self.add_active_cell(c)
                cell.remove_entity_callback = lambda c: self.remove_active_cell(c)
                cell.neighbors = self.get_neighbors_of(cell)

    @property
    def cells(self) -> Iterable:
        """Return all cells iterator"""
        return self.active_cells

    def add_active_cell(self, cell) -> None:
        """Add active cell"""
        self.active_cells.add(cell)

    def remove_active_cell(self, cell) -> None:
        """Add active cell"""
        self.active_cells.remove(cell)

    def place_entity(self, entity, x: int, y: int) -> None:
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

    def get_neighbors_of(self, cell) -> list:
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


"""Cell"""


class Cell:
    """
    Cell - entity that can contain either biological cell
    or other entity
    """

    __dict__ = [
        "x",
        "y",
        "_entity",
        "neighbors",
        "add_entity_callback",
        "remove_entity_callback",
    ]

    def __init__(self, x: int, y: int, entity=None) -> None:
        """Initialize cell"""
        self.x = x
        self.y = y
        self._entity = entity
        self.neighbors = []

        self.add_entity_callback = None
        self.remove_entity_callback = None

    @property
    def entity(self):
        """Return entity"""
        return self._entity

    @entity.setter
    def entity(self, entity_) -> None:
        if self.empty and entity_ is not None:
            self.add_entity_callback(self)

        if entity_ is None and not self.empty:
            self.remove_entity_callback(self)

        self._entity = entity_

    @property
    def empty(self) -> bool:
        """Return true if cell is empty"""
        return self.entity is None

    @property
    def entity_id(self) -> int:
        """Return identifier of the entity"""
        return self.entity.ID if self.entity else 0

    @property
    def color(self):
        if self.entity:
            return self.entity.color
        # return "#000"
        return 0, 0, 0

    def get_free_neighbor(self):
        """Return empty cell"""
        return [cell for cell in self.neighbors if cell.empty]


"""Entities"""

from random import random, choice


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
        if not free_neighbor:
            return

        cell = free_neighbor[0]
        self.move_to(cell)


class BiologicalCell(Entity):
    """Biological cell"""

    ID = 1

    __dict__ = ["ID", "proliferation_potential", "cell", "neighbors", "free_neighbors"]

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
        free_neighbors = self.free_neighbors

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
        # return "#fff"
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
        # return "#ffffff"


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

    @property
    def color(self):
        return (255, 255, 51)


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

    @property
    def color(self):
        return (255, 51, 255)


import pygame
import sys
import pickle

sys.setrecursionlimit(10**6)


from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    BLOCK_SIZE_DIVISIBLE,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    BUTTON_ADD,
    BUTTON_START,
    BUTTON_STOP,
)

from multiprocessing import Pool, Process
import concurrent.futures
from collections import deque

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

simulations = []
running_sim = False
curr_type = 1


class Simulation:
    def __init__(self, x: int, y: int, height: int, width: int):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.block_size = BLOCK_SIZE_DIVISIBLE / height
        self.automaton = FiniteAutomaton(Grid(width, height))
        self.automaton.grid.place_entity(BiologicalCell(), 10, 10)

        self.queue = deque()

        for row in range(self.height):
            pygame.draw.rect(
                screen,
                (178, 190, 181),
                pygame.Rect(self.x, self.y + row, 1, 1),
            )
            pygame.draw.rect(
                screen,
                (178, 190, 181),
                pygame.Rect(self.x + self.width + 1, self.y + row, 1, 1),
            )
        for col in range(self.height):
            pygame.draw.rect(
                screen,
                (178, 190, 181),
                pygame.Rect(self.x + col, self.y, 1, 1),
            )
            pygame.draw.rect(
                screen,
                (178, 190, 181),
                pygame.Rect(self.x + col, self.y + self.height + 1, 1, 1),
            )

        self.x += 1
        self.y += 1

    def calc_steps(self, amount: int):
        for _ in range(amount):
            self.automaton.next()
            self.queue.append(self.automaton.grid.cells)

    def draw(self):
        if len(self.queue) == 0:
            return

        for cell in self.queue.popleft():
            pygame.draw.rect(
                screen,
                cell.entity.color,
                pygame.Rect(
                    self.x + cell.x * self.block_size,
                    self.y + cell.y * self.block_size,
                    self.block_size,
                    self.block_size,
                ),
            )

        # self.automaton.next()


def step_calculator(sim):
    print("smth")
    for _ in range(5):
        sim.automaton.next()
        sim.queue.append(sim.automaton.grid.cells)
        print((sim.queue))


if __name__ == "__main__":
    pygame.init()

    simulations = [
        Simulation(10, 10, 500, 500),
        # Simulation(550, 10, 500, 500),
        # Simulation(10, 550, 500, 500),
        # Simulation(550, 550, 500, 500),
    ]

    print(pickle.dumps(BiologicalCell()))
    print(pickle.dumps(Grid()))
    print(pickle.dumps(simulations[0].automaton.grid.grid))

    exit()
    new_process = Process(target=step_calculator, args=(simulations[0],))
    new_process.start()

    with Pool() as pool:
        res = pool.imap(step_calculator, simulations)

        for piece_of_shit in res:
            print(piece_of_shit)
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    # executor.submit(step_calculator, simulations)

    while True:
        for sim in simulations:
            sim.draw()
            # sim.render_step()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # for sim in simulations:
                # sim.procces.join()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                running_sim = not running_sim

        # start = perf_counter()

        pygame.display.update()
        # pygame.display.flip()
        clock.tick()
