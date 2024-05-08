"""
Super pygame visualisation with multiprocessing backed up with rust, C and C++ at the same time.
"""

from multiprocessing import Process, Queue, Value
import sys
import pygame


from grid import Grid
from automaton import FiniteAutomaton
from entity import BiologicalCell, RTCCell, ClonogenicStemCell, TrueStemCell

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


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

running_sim = Value("b", 0)


class Simulation:
    def __init__(self, x: int, y: int, height=500, width=500, start_x=200, start_y=200):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.block_size = BLOCK_SIZE_DIVISIBLE / height
        self.automaton = FiniteAutomaton(Grid(width, height))
        self.automaton.grid.place_entity(BiologicalCell(), start_x, start_y)

        self.queue = Queue()

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

    def draw(self):
        if self.queue.empty() or not running_sim.value:
            return

        for x, y, color in self.queue.get():
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    self.x + x * self.block_size,
                    self.y + y * self.block_size,
                    self.block_size,
                    self.block_size,
                ),
            )


def step_calculator(queue, active, *args):
    sim_ = Simulation(*args)
    while True:
        if queue.empty() and active.value:
            sim_.automaton.next()
            queue.put(sim_.automaton.grid.coloured_cells)


if __name__ == "__main__":
    pygame.init()

    simulations = [
        Simulation(10, 10, 500, 500),
        Simulation(550, 10, 500, 500, 50, 50),
        Simulation(10, 550, 500, 500, 400, 400),
        Simulation(550, 550, 500, 500, 250, 490),
    ]

    processes = []
    simulations_coords = [
        (10, 10, 500, 500, 250, 250),
        (550, 10, 500, 500, 50, 50),
        (10, 550, 500, 500, 400, 400),
        (550, 550, 500, 500, 250, 490),
    ]

    for sim, coords in zip(simulations, simulations_coords):
        new_process = Process(
            target=step_calculator, args=(sim.queue, running_sim) + coords
        )
        new_process.start()

    print("completed")

    while True:
        for sim in simulations:
            sim.draw()
            # sim.render_step()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for sim in simulations:
                    sim.join()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                running_sim.value = (running_sim.value + 1) % 2

        # start = perf_counter()

        pygame.display.update()
        # pygame.display.flip()
        clock.tick()
