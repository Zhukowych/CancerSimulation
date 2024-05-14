"""
Super pygame visualisation with multiprocessing backed up with rust, C and C++ at the same time.
"""

from multiprocessing import Process, Queue, Value
import sys
import os
import pygame
import pygame_chart as pyc

from automaton import FiniteAutomaton
from grid import Grid
from entity import TrueStemCell, ImmuneCell
from variables import Variables

from constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

# IN GAME constants
BETWEEN_IND = SCREEN_WIDTH // 190, SCREEN_HEIGHT // 50  # x, y


GRID_SIZE = (
    ((SCREEN_WIDTH // 2) - BETWEEN_IND[0] * 3) // 2,
    ((SCREEN_HEIGHT - BETWEEN_IND[1] * 3) // 2),
)  # x,y

GRID_SIZE = min(GRID_SIZE), min(GRID_SIZE)


DASHBOARD_X_Y = 0, BETWEEN_IND[1] * 3 + GRID_SIZE[1] * 2 + 4
DASHBOARD_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT - GRID_SIZE[1] * 2 - BETWEEN_IND[1] - 4


print(BETWEEN_IND, GRID_SIZE)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
text_font = pygame.font.SysFont("monospace", 30)

running_sim = Value("i", 0)


class Simulation:
    """
    Class
    """
    frame_number = 0
    simulation_number = 1

    def __init__(self, x: int, y: int, name="Unnamed"):
        """
        init func
        """
        self.simulation_number = Simulation.simulation_number
        Simulation.simulation_number += 1

        self.counter = None

        self.x = x
        self.y = y
        self.name = name

        self.queue = Queue()

        self.x += 1
        self.y += 1

    def draw(self):
        """
        draws cells
        """
        if self.queue.empty() or not running_sim.value:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            pygame.Rect(self.x, self.y, GRID_SIZE[0], GRID_SIZE[1]),
        )

        # pygame.draw.rect(
        # screen,
        # (255, 255, 255),
        # pygame.Rect(self.x, self.y + GRID_SIZE[1] + 2, 500, BETWEEN_IND[1]),
        # )

        # TODO
        grid, days, self.counter = self.queue.get()

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
            self.name, self.x, self.y + GRID_SIZE[1] + 2, font_size=BETWEEN_IND[1] // 2
        )

    # Capture screenshots into given folder
    def capture_screenshots(self, filepath: str):
        """
        Create a video from the screenshots.
        """
        if os.path.exists(filepath):
            capture_rect = pygame.Rect(self.x, self.y, (GRID_SIZE[0] if not GRID_SIZE[0]%2 else GRID_SIZE[0]+1), (GRID_SIZE[1] if not GRID_SIZE[1]%2 else GRID_SIZE[1]+1))
            subsurface = screen.subsurface(capture_rect)
            pygame.image.save(subsurface, f'{filepath}/Simulation{self.simulation_number}_{self.frame_number:05d}.png')
            self.frame_number += 1

    # Delete all screenshots in the given folder (deletes all .png files!)
    def delete_screenshots(self, filepath: str):
        """
        Delete all screenshots from past simulations.
        """
        if os.path.exists(filepath):
            for filename in os.listdir(filepath):
                file_path = os.path.join(filepath, filename)
                if (os.path.isfile(file_path) or os.path.islink(file_path)) and filename.endswith('.png'):
                    os.unlink(file_path)


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
        self.figure.set_ylim((0, 5000))
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
        text_font.render(f"FPS: {fps_num}", False, (0, 255, 0)),
        (x, y),
    )


def render_sim_status(x: int, y: int):
    """
    render function for printing sim status
    """
    pygame.draw.rect(
        screen,
        (174, 198, 207),
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

    automaton = FiniteAutomaton(Grid(GRID_SIZE[1], GRID_SIZE[0]), Variables())
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

    text_font = pygame.font.SysFont("monospace", font_size)

    pygame.draw.rect(
        screen,
        background_color,
        pygame.Rect(x, y, rect_size_x, rect_size_y),
    )

    screen.blit(
        text_font.render(text, False, text_color),
        (x, y),
    )


if __name__ == "__main__":
    pygame.init()

    simulations = [
        Simulation(BETWEEN_IND[0], BETWEEN_IND[1], "simulation 1"),
        Simulation(
            BETWEEN_IND[0] + GRID_SIZE[0] + 2 + BETWEEN_IND[0],
            BETWEEN_IND[1],
            "simulation 2",
        ),
        Simulation(
            BETWEEN_IND[0],
            BETWEEN_IND[1] + GRID_SIZE[1] + 2 + BETWEEN_IND[1],
            "simulation 3",
        ),
        Simulation(
            BETWEEN_IND[0] + GRID_SIZE[0] + 2 + BETWEEN_IND[0],
            BETWEEN_IND[1] + GRID_SIZE[1] + 2 + BETWEEN_IND[1],
            "simulation 4",
        ),
    ]

    charts = [Chart(i, sim) for i, sim in enumerate(simulations)]

    processes = []

    for sim in simulations:
        new_process = Process(
            target=step_calculator,
            args=(sim.queue, running_sim, GRID_SIZE[0] // 2, GRID_SIZE[1] // 2),
        )
        new_process.start()

    prepare_board()

    while True:

        for chart in charts:
            chart.draw()

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
        # render_fps(DASHBOARD_X_Y[0], DASHBOARD_X_Y[1], int(clock.get_fps()))
        render_text(
            "FPS: " + str(int(clock.get_fps())),
            DASHBOARD_X_Y[0],
            DASHBOARD_X_Y[1],
            20,
            (174, 198, 207),
            (0, 255, 0),
        )
        render_sim_status(SCREEN_WIDTH - 200, DASHBOARD_X_Y[1])
