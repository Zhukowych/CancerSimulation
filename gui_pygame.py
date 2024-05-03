import pygame
import sys

from grid import Grid
from automaton import FiniteAutomaton
from entity import BiologicalCell

from time import perf_counter


class MainWindow:
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.block_size = int(1000 / height)

        cell = BiologicalCell()

        grid = Grid(width, height)
        self.automaton = FiniteAutomaton(grid)

        grid.place_entity(cell, 2, 2)

    def render(self, screen_):
        for i in range(self.height):
            for j in range(self.width):
                cell_rect = pygame.Rect(
                    i * self.block_size,
                    j * self.block_size,
                    self.block_size,
                    self.block_size,
                )
                pygame.draw.rect(
                    screen_, self.automaton.grid.grid[i][j].color, cell_rect
                )

        self.automaton.next()


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()

    window = MainWindow(100, 100)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            start = perf_counter()

            window.render(screen)
            pygame.display.update()
            clock.tick()
            print(perf_counter() - start)
