import pygame
import sys

sys.setrecursionlimit(10**6)

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

from multiprocessing import Pool
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
    for i in range(100):
        print(i)
    for _ in range(100):
        print(sim.queue)
        sim.automaton.next()
        sim.queue.append(sim.automaton.grid.cells)
        print(sim.queue)


if __name__ == "__main__":
    pygame.init()

    simulations = [
        Simulation(10, 10, 500, 500),
        # Simulation(550, 10, 500, 500),
        # Simulation(10, 550, 500, 500),
        # Simulation(550, 550, 500, 500),
    ]

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
