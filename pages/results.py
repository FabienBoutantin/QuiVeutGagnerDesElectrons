#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines results Page classes for a quiz game using the Pygame
library.

Classes:
    GoodAnswerPage: Represents the screen displayed when the player selects
                    the correct answer.
    BadAnswerPage: Represents the screen displayed when the player selects the
                   wrong answer.
"""


from time import time
import pygame

from config import WIDTH, HEIGHT, QUESTION_HEIGHT, QUESTION_SPAN, \
                   ANSWER_LINE_COLOR, QUESTION_TEXT_COLOR, \
                   GOOD_TEXT_COLOR, BAD_TEXT_COLOR
from fonts import fonts
from pages.base_page import Page
from utils import BackToQuestionException, StartupException


# Top, left, width, height
QUESTION_RECT = pygame.Rect(
    (QUESTION_SPAN, HEIGHT // 2 - QUESTION_HEIGHT // 2),
    (WIDTH - QUESTION_SPAN * 2, QUESTION_HEIGHT)
)


class GoodAnswerPage(Page):
    """
    Represents the screen displayed when the player selects the correct answer.
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(
            self, question, answer,
            text="Bonne réponse !", color=GOOD_TEXT_COLOR,
            exception=BackToQuestionException,
            time_to_wait=4
    ):
        """
        Initializes the GoodAnswerPage object with the given question, answer,
        text, color, exception, and time to wait.
        """
        super().__init__()
        self.exception = exception
        self.time_to_wait = time_to_wait
        self.start_time = time()
        self.title_surface = fonts.big().render(
            text, True, color
        ).convert_alpha()
        self.question_surface = fonts.normal().render(
            question.text, True, QUESTION_TEXT_COLOR
        ).convert_alpha()
        self.answer_surface = fonts.normal().render(
            question.answers[answer], True, ANSWER_LINE_COLOR
        ).convert_alpha()

    def draw(self, screen, cur_time, dt):
        """
        Draws the good answer screen on the given screen.
        """
        if cur_time - self.start_time > self.time_to_wait:
            raise self.exception()
        self.animate_surf_v(
            screen, self.title_surface, cur_time, self.start_time, 2
        )

        screen.blit(
            self.question_surface,
            (
                WIDTH // 2 - self.question_surface.get_width() // 2,
                int(HEIGHT * 0.4)
            )
        )

        screen.blit(
            self.answer_surface,
            (
                WIDTH // 2 - self.answer_surface.get_width() // 2,
                HEIGHT // 2
            )
        )

    def handle_event(self, event):
        """
        Handles the given event.
        """
        go_back = \
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE \
            or \
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 3
        if go_back:
            raise self.exception()


class BadAnswerPage(GoodAnswerPage):
    """
    Represents the screen displayed when the player selects the wrong answer.
    """
    def __init__(
        self, question, answer,
        text="Mauvaise réponse !", color=BAD_TEXT_COLOR
    ):
        """
        Initializes the BadAnswerPage object with the given question, answer,
        text, and color.
        """
        super().__init__(question, answer, text, color, StartupException, 8)
        good_answer = question.answers[question.correct_answer]
        self.good_answer_surface = fonts.normal().render(
            good_answer, True, GOOD_TEXT_COLOR
        ).convert_alpha()

    def draw(self, screen, cur_time, dt):
        """
        Draws the bad answer screen on the given screen.
        """
        super().draw(screen, cur_time, dt)
        if cur_time - self.start_time > 2:
            pygame.draw.line(
                screen, BAD_TEXT_COLOR,
                (
                    (WIDTH - self.answer_surface.get_width()) // 2,
                    HEIGHT // 2 + self.answer_surface.get_height()
                ),
                (
                    (WIDTH + self.answer_surface.get_width()) // 2,
                    HEIGHT // 2
                ),
                8
            )
            screen.blit(
                self.good_answer_surface,
                (
                    WIDTH // 2 - self.good_answer_surface.get_width() // 2,
                    int(HEIGHT / 2 + self.answer_surface.get_height() * 1.5)
                )
            )
