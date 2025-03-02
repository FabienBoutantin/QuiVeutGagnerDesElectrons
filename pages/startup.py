#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines various game phase Page classes for a quiz game using the
Pygame library.

Classes:
    StartUpPage: Represents the startup screen of the game.
    VictoryPage: Represents the screen displayed when the player wins the game.
"""


from pathlib import Path
from time import time
import pygame

from config import WIDTH, HEIGHT, \
    ANSWER_SELECTION_COLOR, DEFAULT_TEXT_COLOR, GOOD_TEXT_COLOR
from fonts import fonts
from pages.base_page import Page
from sparkles import Sparkles
from utils import BackToQuestionException, StartupException
from utils import ease_out, clamp, get_logo_surf


class StartUpPage(Page):
    """
    Represents the startup screen of the game.
    """
    def __init__(self):
        """
        Initializes the StartUpPage object.
        """
        super().__init__()
        self.animate_to_question = False
        self.logo_surface = get_logo_surf()
        self.logo_x = (WIDTH - self.logo_surface.get_size()[0]) // 2
        self.logo_y = HEIGHT // 2 - self.logo_surface.get_size()[1]
        self.logo_y //= 2
        self.logo_y -= 20
        self.start_time = time()
        self.title_surface = fonts.big().render(
            "Bienvenue pour jouer à", True, DEFAULT_TEXT_COLOR
        )
        pygame.mouse.set_visible(False)

    def draw(self, screen, cur_time, dt):
        """
        Draws the startup screen on the given screen.
        """
        if self.animate_to_question:
            if cur_time - self.start_time > 2.5:
                pygame.mouse.set_visible(True)
                pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
                raise BackToQuestionException()
        else:
            self.animate_surf_v(
                screen, self.title_surface, cur_time, self.start_time, 2
            )

        src_x = - self.logo_surface.get_width()
        target_x = self.logo_x
        src_y = HEIGHT * 0.7 - self.logo_surface.get_height() * 0.5
        target_y = self.logo_y
        if self.animate_to_question:
            factor = clamp((cur_time - self.start_time) / 2, 0, 1)
            title_offset_x = target_x
            title_offset_y = ease_out(
                src_y, target_y,
                factor
            )
        else:
            factor = clamp((cur_time - self.start_time - 2.5) / 2, 0, 1)
            title_offset_x = ease_out(
                src_x, target_x,
                factor
            )
            title_offset_y = src_y

        screen.blit(
            self.logo_surface,
            (int(title_offset_x), int(title_offset_y))
        )

    def handle_event(self, event):
        """
        Handles the given event.
        """
        if not self.animate_to_question \
                and event.type == pygame.MOUSEBUTTONDOWN:
            self.animate_to_question = True
            self.start_time = time()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            pygame.mouse.set_visible(True)
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
            raise BackToQuestionException()


class VictoryPage(Page):
    """
    Represents the screen displayed when the player wins the game.
    """
    def __init__(self):
        """
        Initializes the VictoryPage object.
        """
        super().__init__()
        self.start_time = time()
        texts = (
            ("Bravo ! Vous avez gagné !", GOOD_TEXT_COLOR),
            ("Vous pouvez maintenant participer", DEFAULT_TEXT_COLOR),
            ("à ce projet de quartier !", DEFAULT_TEXT_COLOR),
            ("", (0, 0, 0)),
            ("Plus d'informations sur :", ANSWER_SELECTION_COLOR),
            ("https://www.clairvolt.fr", ANSWER_SELECTION_COLOR),
        )
        self.surfaces = []
        for txt, color in texts:
            self.surfaces.append(fonts.big().render(txt, True, color))

        sparkle_surfs = []
        for p in sorted(Path("assets").glob("confetti*.png")):
            surf = pygame.image.load(str(p))
            surf.set_alpha(200)
            sparkle_surfs.append(surf)
        self.sparkles = Sparkles(sparkle_surfs, 300, gravity=1)

    def draw(self, screen, cur_time, dt):
        """
        Draws the victory screen on the given screen.
        """
        if cur_time - self.start_time > 10:
            raise StartupException()

        self.sparkles.draw(screen)

        y_start = HEIGHT // 4
        for surface in self.surfaces:
            screen.blit(
                surface,
                (
                    (WIDTH - surface.get_width()) // 2,
                    y_start
                )
            )
            y_start += surface.get_height() + 10

    def handle_event(self, event):
        """
        Handles the given event.
        """
