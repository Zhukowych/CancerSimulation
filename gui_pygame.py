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

        self.grid = Grid(width, height)
        self.automaton = FiniteAutomaton(self.grid)

        self.grid.place_entity(cell, 2, 2)

    def render(self, screen_):
        for cell in self.grid.cells:
            cell_rect = pygame.Rect(
                cell.x * self.block_size,
                cell.y * self.block_size,
                self.block_size,
                self.block_size,
            )
            pygame.draw.rect(
                screen_, cell.color, cell_rect
            )

        start = perf_counter()  
        self.automaton.next()
        print("Automaton step:", perf_counter() - start, len(self.grid.cells))


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()

    window = MainWindow(500, 500)

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
