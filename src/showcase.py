"""
Super pygame visualisation with multiprocessing backed up with rust, C and C++ at the same time.
"""

from multiprocessing import Process, Queue, Value, Event
from collections import deque
import pygame
import pygame_chart as pyc

import pygame
import argparse
from .automaton import FiniteAutomaton
from .grid import Grid
from .entity import TrueStemCell, ImmuneCell
from .variables import Variables, read_variables

from .constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

# IN GAME constants
BETWEEN_IND = SCREEN_WIDTH // 170, SCREEN_HEIGHT // 30  # x, y


GRID_SIZE = (
    ((SCREEN_WIDTH // 2) - BETWEEN_IND[0] * 3) // 2,
    ((SCREEN_HEIGHT - BETWEEN_IND[1] * 3) // 2),
)  # x,y

GRID_SIZE = min(GRID_SIZE), min(GRID_SIZE)

BETWEEN_IND = 50, 50
GRID_SIZE = 1000, 1000


DASHBOARD_X_Y = 0, BETWEEN_IND[1] * 3 + GRID_SIZE[1] * 2 + 4
DASHBOARD_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT - GRID_SIZE[1] * 2 - BETWEEN_IND[1] - 4


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
screen.fill((255, 255, 255))
text_font = pygame.font.SysFont("monospace", 30, bold=True)

running_sim = Value("i", 0)


class Simulation:
    """
    Class
    """

    def __init__(self, x: int, y: int, name="Unnamed"):
        """
        init func
        """
        self.counter = None

        self.x = x
        self.y = y
        self.name = name

        self.queue = None

        self.x += 1
        self.y += 1

        self.days = 0

    def draw(self):
        """
        draws sells
        """
        if len(self.queue) == 0 or not running_sim.value:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, GRID_SIZE[0], GRID_SIZE[1]),
        )

        grid, days, self.counter = self.queue.popleft()
        self.days = days

        for x, y, color in grid:
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    self.x + x * 2,
                    self.y + y * 2,
                    2,
                    2,
                ),
            )

    @property
    def has_frames(self) -> bool:
        """Return True if queue has elements"""
        return bool(len(self.queue))


def main():
    argument_parser = argparse.ArgumentParser(description="Cancer simulation.")

    argument_parser.add_argument("config_file", type=str)
    args = argument_parser.parse_args()

    simulation_variables = read_variables(args.config_file)
    variables = simulation_variables[0]

    sim = Simulation(BETWEEN_IND[0], BETWEEN_IND[1], variables.name)

    automaton = FiniteAutomaton(Grid(GRID_SIZE[1] // 2, GRID_SIZE[0] // 2), variables)
    automaton.grid.place_entity(
        TrueStemCell(proliferation_potential=variables.max_proliferation_potential),
        250,
        250,
    )
    automaton.grid.place_entity(ImmuneCell(), 1, 1)

    queue = deque()
    sim.queue = queue

    pygame.init()

    processes = []

    pygame.display.set_caption("Cancer simulation")
    run = True

    while run:

        automaton.next()
        queue.append(
            (
                automaton.grid.coloured_cells,
                automaton.variables.days_elapsed,
                automaton.counter,
            )
        )

        sim.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                run = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                running_sim.value = (running_sim.value + 1) % 2

        pygame.display.update()
        clock.tick()
    for process in processes:
        process.kill()

    pygame.quit()
