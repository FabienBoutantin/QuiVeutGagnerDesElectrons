#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
main.py

This module contains the main game logic for "Qui Veut Gagner des Electrons !".
It initializes the game, handles events, and manages the game loop.

Classes:
    Game: Manages the game state, including questions, pages, and background
          effects.

Functions:
    init_pygame(): Initializes pygame, sets up the display mode, and returns
                   the screen and clock.
    handle_events(current_page): Handles pygame events and delegates them to
                                 the current page.
    main(): The main function that initializes the game, runs the game loop,
            and handles cleanup.
"""


from time import time
from math import sin, cos
from os import chdir
from pathlib import Path
from sys import argv as sys_argv
from psutil import Process as psutil_Process
import pygame
from sparkles import Sparkles

from config import WIDTH, HEIGHT, SPARKLE_COUNT
from config import BACKGROUND_COLOR, BACKGROUND_COLOR2
from fonts import fonts
from pages import StartUpPage, QuestionPage, \
    GoodAnswerPage, BadAnswerPage, VictoryPage, \
    FiftyPage, PhonePage, PublicPage
from questions import QuestionList
from utils import gradient_rect, interp_color
from utils import VictoryException, GoodAnswerException, \
    BadAnswerException, BackToQuestionException, StartupException, \
    FiftyException, PhoneException, PublicException


def init_pygame():
    """
    Initializes pygame, sets up the display mode, and returns the screen and
    clock.
    """
    pygame.init()
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    flags = pygame.SCALED
    if "-f" in sys_argv:
        flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=flags)
    pygame.display.set_caption("Qui Veut Gagner des Electrons !")
    return screen, pygame.time.Clock()


def handle_events(current_page):
    """
    Handles pygame events and delegates them to the current page.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and \
                    pygame.key.get_mods() & pygame.KMOD_CTRL:
                return False
        current_page.handle_event(event)
    return True


# pylint: disable=too-many-instance-attributes
class Game:
    """
    Manages the game state, including questions, pages, and background effects.
    """
    __slots__ = (
        "questions", "question_page", "current_page",
        "sparkles",
        "footer_surf", "footer_x", "footer_y",
        "dynamic_background"
    )

    def __init__(self, dynamic_background=True):
        """
        Initializes the game state.
        """
        self.questions = QuestionList()
        self.question_page = QuestionPage(self.questions)
        self.question_page.update_question()
        self.current_page = StartUpPage()

        self.footer_surf = fonts.small().render(
            "Plus d'informations sur : https://www.clairvolt.fr",
            True,
            (128, 128, 128)
        )
        self.footer_x = 0
        self.footer_y = HEIGHT - self.footer_surf.get_height() - 4

        transp_surf = pygame.surface.Surface((1, 1))
        transp_surf.set_alpha(0)
        sparkle_surfs = [transp_surf for _ in range(4)]
        for p in sorted(Path("assets").glob("sparkle*.png")):
            surf = pygame.image.load(str(p))
            surf.set_alpha(200)
            sparkle_surfs.append(surf)
        self.sparkles = Sparkles(sparkle_surfs, SPARKLE_COUNT)
        self.dynamic_background = dynamic_background

    def fill_background(self, screen, cur_time):
        """
        Fills the background with a gradient and draws the sparkles.
        """
        if self.dynamic_background:
            gradient_rect(
                screen,
                (
                    interp_color(
                        BACKGROUND_COLOR, BACKGROUND_COLOR2,
                        (1.0 + sin(cur_time/2)) / 2
                    ),
                    interp_color(
                        (0, 0, 0), BACKGROUND_COLOR2,
                        (1.0 + cos(cur_time/3)) / 2
                    ),
                    interp_color(
                        BACKGROUND_COLOR, (0, 0, 0),
                        (1.0 + cos(cur_time/7)) / 2
                    ),
                    interp_color(
                        BACKGROUND_COLOR, BACKGROUND_COLOR2,
                        1.0 - (1.0 + sin(cur_time/2.5)) / 2
                    ),
                ),
                pygame.Rect(0, 0, WIDTH, HEIGHT)
            )
            self.sparkles.draw(screen)
        else:
            screen.fill(BACKGROUND_COLOR)

        self.footer_x += 0.001
        screen.blit(
            self.footer_surf,
            (int(cos(self.footer_x) * WIDTH), self.footer_y)
        )

    def reset(self):
        """
        Resets the game state.
        """
        self.questions.reset()

    def step(self, screen, cur_time, dt) -> bool:
        """
        Advances the game state by one frame.
        """
        try:
            if not handle_events(self.current_page):
                return True
            self.fill_background(screen, cur_time)
            self.current_page.draw(screen, cur_time, dt)
        except StartupException:
            self.current_page = StartUpPage()
            self.reset()
        except BackToQuestionException:
            try:
                self.question_page.update_question()
                self.current_page = self.question_page
            except VictoryException:
                # if we reach the end of the questions
                self.current_page = VictoryPage()
        except VictoryException:
            self.current_page = VictoryPage()
        except GoodAnswerException as e:
            self.current_page = GoodAnswerPage(e.question, e.answer)
        except BadAnswerException as e:
            self.current_page = BadAnswerPage(e.question, e.answer)
        except FiftyException as e:
            self.current_page = FiftyPage(e.question)
        except PhoneException as e:
            self.current_page = PhonePage(e.question)
        except PublicException as e:
            self.current_page = PublicPage(e.question)
        return False


def main():
    """
    The main function that initializes the game, runs the game loop, and
    handles cleanup.
    """
    # Ensure all assets can be found
    chdir(Path(__file__).parent)

    # Initialize game engine
    screen, clock = init_pygame()
    fonts.init()

    # Start the game
    game = Game(
        dynamic_background="-l" not in sys_argv
    )
    count = 0
    start_time = time()
    while True:
        if game.step(screen, time(), clock.get_time()):
            break

        count += 1

        # if time() - start_time > 10:
        #     break
        # print time per image and FPS
        # print("\r", clock.get_time(), clock.get_fps(), end="    ")

        pygame.display.flip()
        clock.tick(60)

    duration = time() - start_time
    print(f"\n{count} images drawn in {duration:.02f} s")
    print(f"  mean: {count / duration:.02f} FPS")
    # print memory usage for this script
    memory = psutil_Process().memory_info().rss / 1024 / 1024
    print(f"Top memory usage: {memory:.2f} MB")

    pygame.quit()
    print("Exit!")


if __name__ == "__main__":
    main()
