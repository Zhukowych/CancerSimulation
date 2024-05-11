"""
Super pygame visualisation with multiprocessing backed up with rust, C and C++ at the same time.
"""

import sys
from multiprocessing import Process, Queue, Value

import pygame
import argparse
from automaton import FiniteAutomaton
from grid import Grid
from entity import TrueStemCell, ImmuneCell
from variables import Variables

from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    BLOCK_SIZE_DIVISIBLE,
)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
text_font = pygame.font.SysFont("monospace", 30)

running_sim = Value("i", 0)


class Simulation:
    """
    Class
    """

    def __init__(self, x: int, y: int, height=500, width=500):
        """
        init func
        """
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.block_size = BLOCK_SIZE_DIVISIBLE / height

        self.queue = Queue()

        self.x += 1
        self.y += 1

    def draw(self):
        """
        draws sells
        """
        if self.queue.empty() or not running_sim.value:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, BLOCK_SIZE_DIVISIBLE, BLOCK_SIZE_DIVISIBLE),
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y + 502, 500, 30),
        )

        # TODO
        grid, days, cell_counter = self.queue.get()

        for x, y, color in grid:
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

        screen.blit(
            text_font.render(f"D: {days} days", False, (0, 0, 0)),
            (self.x, self.y + 502),
        )


def prepare_board():
    """
    renders board
    """

    screen.fill((255, 255, 255))
    pygame.display.flip()

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(502, 0, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 502, 502, 1))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 0, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 0, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(1042, 0, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 502, 502, 1))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 540, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 540, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 1042, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(502, 540, 1, 502))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 540, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 540, 1, 502))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(540, 1042, 502, 1))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(1042, 540, 1, 502))


def render_fps(x: int, y: int, fps_num: int):
    """
    render function to render fps
    """

    pygame.draw.rect(
        screen,
        (255, 255, 255),
        pygame.Rect(x, y, 300, 150),
    )

    screen.blit(
        text_font.render(f"FPS: {fps_num}", False, (0, 255, 0)),
        (x, y),
    )


def render_sim_status(x: int, y: int):
    """
    render function for printing sim status
    """
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        pygame.Rect(x, y, 300, 400),
    )

    if running_sim.value:
        screen.blit(
            text_font.render("Running", False, (0, 255, 0)),
            (x, y),
        )
    else:
        screen.blit(
            text_font.render("Stopped", False, (255, 0, 0)),
            (x, y),
        )


def step_calculator(queue, active, start_x, start_y):
    """
    Calculates a steps for each process. Creates an automaton and calculates one step at a time.
    Puts in queue: list of [coordinates of active cells with their respective color, days elapsed,
    CellCunter(for graphs)]
    """

    automaton = FiniteAutomaton(Grid(500, 500), Variables())
    automaton.grid.place_entity(TrueStemCell(), start_x, start_y)
    automaton.grid.place_entity(ImmuneCell(), 1, 1)
    while True:
        if queue.empty() and active.value:
            automaton.next()
            automaton.variables.time_step()
            queue.put(
                (
                    automaton.grid.coloured_cells,
                    automaton.variables.days_elapsed,
                    automaton.counter,
                )
            )


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Cancer simulation.")

    argument_parser.add_argument("config_file", type=str, required=True)
    args = argument_parser.parse_args()

    pygame.init()

    simulations = [
        Simulation(0, 0, 410, 510),
        Simulation(540, 0, 500, 500),
        Simulation(0, 540, 500, 500),
        Simulation(540, 540, 500, 500),
    ]

    processes = []

    for sim in simulations:
        new_process = Process(
            target=step_calculator, args=(sim.queue, running_sim, 250, 250)
        )
        new_process.start()

    prepare_board()

    while True:
        for sim in simulations:
            sim.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for sim in processes:
                    sim.kill()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                running_sim.value = (running_sim.value + 1) % 2

            if event.type == pygame.VIDEORESIZE or event.type == pygame.VIDEOEXPOSE:
                prepare_board()

        pygame.display.update()
        clock.tick()
        render_fps(1700, 100, int(clock.get_fps()))
        render_sim_status(1700, 900)
