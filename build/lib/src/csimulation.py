"""
Super pygame visualisation with multiprocessing backed up with rust, C and C++ at the same time.
"""

import sys
from multiprocessing import Process, Queue, Value
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


DASHBOARD_X_Y = 0, BETWEEN_IND[1] * 3 + GRID_SIZE[1] * 2 + 4
DASHBOARD_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT - GRID_SIZE[1] * 2 - BETWEEN_IND[1] - 4



screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
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

        self.queue = Queue()

        self.x += 1
        self.y += 1

        self.days = 0

    def draw(self):
        """
        draws sells
        """
        if self.queue.empty() or not running_sim.value:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, GRID_SIZE[0], GRID_SIZE[1]),
        )

        grid, days, self.counter = self.queue.get()
        self.days = days

        for x, y, color in grid:
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(
                    self.x + x,
                    self.y + y,
                    1,
                    1,
                ),
            )

        render_text(
            self.name, self.x, self.y + GRID_SIZE[1] + 2, font_size=int(BETWEEN_IND[1] // 1.6)
        )

    @property
    def has_frames(self) -> bool:
        """Return True if queue has elements"""
        return bool(self.queue.qsize())


class Chart:
    """Represents a chart that displays the number of each cell type over time"""

    def __init__(self, sim_index, simulation: Simulation):
        """
        Initializes the chart
        """
        self.sim = simulation
        self.index = sim_index
        self.figure = pyc.Figure(
            screen,
            self.sim.x + GRID_SIZE[0] * 2 + BETWEEN_IND[0] * 3,
            self.sim.y,
            GRID_SIZE[0],
            GRID_SIZE[1],
        )

    def draw(self):
        """Draws the chart"""
        data = (
            [0, 0, 0, 0]
            if not self.sim.counter
            else [
                self.sim.counter.immune_cell,
                self.sim.counter.tumor_cell,
                self.sim.counter.proliferating_cell,
                self.sim.counter.stem_cell,
            ]
        )
        self.figure.set_ylim((0, 10000))
        self.figure.set_xlim((0, 8))
        self.figure.add_title(f"Simulation {self.index + 1}")
        self.figure.add_legend()
        self.figure.add_gridlines()

        self.figure.bar(
            "Immune, Tumor, Proliferating and Stem cells",
            [1, 3, 5, 7],
            data,
            color=(168, 168, 168),
        )
        self.figure.draw()


def prepare_board():
    """
    renders board
    """

    screen.fill((255, 255, 255))
    pygame.display.flip()

    # FIRST RECT
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(BETWEEN_IND[0], BETWEEN_IND[1], GRID_SIZE[0] + 2, 1),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(BETWEEN_IND[0], BETWEEN_IND[1], 1, GRID_SIZE[1] + 2),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] + GRID_SIZE[0] + 2, BETWEEN_IND[1], 1, GRID_SIZE[1] + 2
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0], BETWEEN_IND[1] + GRID_SIZE[1] + 2, GRID_SIZE[0] + 2, 1
        ),
    )

    # SECOND RECT
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2, BETWEEN_IND[1], GRID_SIZE[0] + 2, 1
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2, BETWEEN_IND[1], 1, GRID_SIZE[1] + 2
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] * 2 + 4,
            BETWEEN_IND[1],
            1,
            GRID_SIZE[1] + 2,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2,
            BETWEEN_IND[1] + GRID_SIZE[1] + 2,
            GRID_SIZE[0] + 2,
            1,
        ),
    )

    # THIRD RECT
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0],
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            GRID_SIZE[0] + 2,
            1,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0],
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            1,
            GRID_SIZE[1] + 2,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] + GRID_SIZE[0] + 2,
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            1,
            GRID_SIZE[1] + 2,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0],
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] * 2 + 4,
            GRID_SIZE[0] + 2,
            1,
        ),
    )

    # FOURTH GRID
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2,
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            GRID_SIZE[0] + 2,
            1,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2,
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            1,
            GRID_SIZE[1] + 2,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] * 2 + 4,
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] + 2,
            1,
            GRID_SIZE[1] + 2,
        ),
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            BETWEEN_IND[0] * 2 + GRID_SIZE[0] + 2,
            BETWEEN_IND[1] * 2 + GRID_SIZE[1] * 2 + 4,
            GRID_SIZE[0] + 2,
            1,
        ),
    )

    # DRAW DASHBOARD
    pygame.draw.rect(
        screen,
        (174, 198, 207),
        pygame.Rect(
            DASHBOARD_X_Y[0], DASHBOARD_X_Y[1], DASHBOARD_SIZE[0], DASHBOARD_SIZE[1]
        ),
    )


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
        text_font.render(f"FPS: {fps_num}", False, (0, 0, 0)),
        (x, y),
    )


def render_sim_status(x: int, y: int):
    """
    render function for printing sim status
    """
    # pygame.draw.rect(
    #     screen,
    #     (174, 198, 207),
    #     pygame.Rect(x, y, 300, 400),
    # )

    if running_sim.value:
        render_text(
            "Status: Running",
            DASHBOARD_X_Y[0] + 120,
            DASHBOARD_X_Y[1] + 5,
            20,
            (174, 198, 207),
            (0, 0, 0),
        )
    else:
        render_text(
            "Status: Stopped",
            DASHBOARD_X_Y[0] + 120,
            DASHBOARD_X_Y[1] + 5,
            20,
            (174, 198, 207),
            (0, 0, 0),
        )      


def step_calculator(variables, queue, active, start_x, start_y):
    """
    Calculates a steps for each process. Creates an automaton and calculates one step at a time.
    Puts in queue: list of [coordinates of active cells with their respective color, days elapsed,
    CellCunter(for graphs)]
    """

    automaton = FiniteAutomaton(Grid(GRID_SIZE[1], GRID_SIZE[0]), variables)
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


def render_text(
    text: str,
    x: int,
    y: int,
    font_size=20,
    background_color=(255, 255, 255),
    text_color=(0, 0, 0),
):
    rect_size_x, rect_size_y = len(text) * font_size, int(font_size * 1.5) + 1

    text_font = pygame.font.SysFont("monospace", font_size, bold=True)

    pygame.draw.rect(
        screen,
        background_color,
        pygame.Rect(x, y, rect_size_x, rect_size_y),
    )

    screen.blit(
        text_font.render(text, False, text_color),
        (x, y),
    )


SIMULATION_SIZES = [
    (BETWEEN_IND[0], BETWEEN_IND[1]),
    (BETWEEN_IND[0] + GRID_SIZE[0] + 2 + BETWEEN_IND[0], BETWEEN_IND[1],),
    (BETWEEN_IND[0], BETWEEN_IND[1] + GRID_SIZE[1] + 2 + BETWEEN_IND[1],),
    (BETWEEN_IND[0] + GRID_SIZE[0] + 2 + BETWEEN_IND[0],
     BETWEEN_IND[1] + GRID_SIZE[1] + 2 + BETWEEN_IND[1],)
]


def main():
    argument_parser = argparse.ArgumentParser(description="Cancer simulation.")

    argument_parser.add_argument("config_file", type=str)
    args = argument_parser.parse_args()

    simulation_variables = read_variables(args.config_file)

    simulations = []

    for i, variables in enumerate(simulation_variables):
        simulations.append(Simulation(*SIMULATION_SIZES[i], variables.name))

    pygame.init()

    charts = [Chart(i, sim) for i, sim in enumerate(simulations)]

    processes = []

    for i, simulation in enumerate(simulations):
        new_process = Process(
            target=step_calculator,
            args=(simulation_variables[i],
                  simulation.queue,
                  running_sim,
                  GRID_SIZE[0] // 2,
                  GRID_SIZE[1] // 2),
        )
        new_process.start()

    prepare_board()

    pygame.display.set_caption("Cancer simulation")

    while True:


        if all(simulation.has_frames for simulation in simulations):
            for chart in charts:
                chart.draw()

            for simulation in simulations:
                simulation.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for simulation in processes:
                    simulation.kill()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                running_sim.value = (running_sim.value + 1) % 2

            if event.type == pygame.VIDEORESIZE or event.type == pygame.VIDEOEXPOSE:
                prepare_board()

        pygame.display.update()
        clock.tick()
        render_text(
            "FPS: " + str(int(clock.get_fps())),
            DASHBOARD_X_Y[0] + 10,
            DASHBOARD_X_Y[1] + 5,
            20,
            (174, 198, 207),
            (0, 0, 0),
        )

        render_sim_status(40, DASHBOARD_X_Y[1])

        render_text(
            "Days elapsed: " + str(simulations[0].days),
            DASHBOARD_X_Y[0] + 320,
            DASHBOARD_X_Y[1] + 5,
            20,
            (174, 198, 207),
            (0, 0, 0),
        )

        render_text(
            "Config filename: " + str(args.config_file),
            DASHBOARD_X_Y[0] + 540,
            DASHBOARD_X_Y[1] + 5,
            20,
            (174, 198, 207),
            (0, 0, 0),
        )