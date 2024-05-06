import pygame
import sys

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

screen = pygame.display.set_mode((SCREEN_WIDTH, 1000))
clock = pygame.time.Clock()

simulations = []
running_sim = False
curr_type = 1

from threading import Thread


class Button:
    def __init__(self, x: int, y: int, image: str):
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y
        self.clicked = False

    def render(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1:
                simulations.append(
                    Simulation(
                        self.rect.x - BLOCK_SIZE_DIVISIBLE // 2,
                        self.rect.y - BLOCK_SIZE_DIVISIBLE // 2,
                        BLOCK_SIZE_DIVISIBLE,
                        BLOCK_SIZE_DIVISIBLE,
                    )
                )
                simulations[-1].render()
                return

        screen.blit(self.image, (self.rect.x, self.rect.y))

    def start_sim(self):

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                global running_sim
                if running_sim:
                    self.image = pygame.image.load(BUTTON_STOP).convert_alpha()
                else:
                    self.image = pygame.image.load(BUTTON_START).convert_alpha()

                tmp_xy = self.rect.x, self.rect.y
                self.rect = self.image.get_rect()
                self.rect.topleft = tmp_xy

                running_sim = not running_sim

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))


class Simulation:

    def __init__(self, x: int, y: int, height: int, width: int):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.block_size = BLOCK_SIZE_DIVISIBLE / height
        self.automaton = FiniteAutomaton(Grid(width, height))

    def render(self):

        pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            if (
                self.x <= pos[0] <= self.x + self.width
                and self.y <= pos[1] <= self.y + self.height
            ):
                if curr_type == 1:
                    self.automaton.grid.place_entity(
                        BiologicalCell(), pos[0] - self.x, pos[1] - self.y
                    )

        for row in range(self.height):
            for col in range(self.width):
                pygame.draw.rect(
                    screen,
                    self.automaton.grid.grid[row][col].color,
                    pygame.Rect(
                        self.x + col * self.block_size,
                        self.y + row * self.block_size,
                        self.block_size,
                        self.block_size,
                    ),
                )


if __name__ == "__main__":
    pygame.init()

    add_button_1 = Button(200, 200, BUTTON_ADD)
    add_button_2 = Button(750, 200, BUTTON_ADD)
    add_button_3 = Button(200, 750, BUTTON_ADD)
    add_button_4 = Button(750, 750, BUTTON_ADD)
    start_button = Button(1300, 200, BUTTON_START)

    while True:
        tmp_threads = []
        N_SIMS = len(simulations)
        if N_SIMS < 4:
            add_button_4.render()
        if N_SIMS < 3:
            add_button_3.render()
        if N_SIMS < 2:
            add_button_2.render()
        if N_SIMS < 1:
            add_button_1.render()

        start_button.start_sim()

        for sim in simulations:
            sim.render()
            if running_sim:
                tmp_threads.append(new_thr := Thread(target=sim.automaton.next))
                new_thr.start()

        if running_sim:
            for thr in tmp_threads:
                thr.join()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # start = perf_counter()

        pygame.display.update()
        # pygame.display.flip()
        clock.tick()
