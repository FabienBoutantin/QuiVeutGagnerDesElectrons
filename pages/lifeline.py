#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines various Page classes for lifeline screens.

Classes:
    FiftyPage: Represents the screen displayed when the player uses the 50:50
               lifeline.
    PhonePage: Represents the screen displayed when the player uses the
               phone-a-friend lifeline.
    PublicPage: Represents the screen displayed when the player uses the
                ask-the-audience lifeline.

"""


from time import time
import pygame

from pages.base_page import Page
from config import WIDTH, HEIGHT, \
    ANSWER_SELECTION_COLOR, DEFAULT_TEXT_COLOR
from fonts import fonts
from utils import BackToQuestionException
from utils import ease_out, clamp


class FiftyPage(Page):
    """
    Represents the screen displayed when the player uses the 50:50 lifeline.
    """
    def __init__(self, question):
        """
        Initializes the FiftyPage object with the given question.
        """
        super().__init__()
        self.start_time = time()
        self.question = question
        texts = [
            ("Vous avez utilisé le 50:50", ANSWER_SELECTION_COLOR),
            ("Vous avez maintenant le choix", DEFAULT_TEXT_COLOR),
            ("entre les deux réponses suivantes", DEFAULT_TEXT_COLOR),
        ]
        for i in question.fifty_fifty:
            texts.append(
                (
                    f'{chr(ord("A") + i)} : {question.answers[i]}',
                    DEFAULT_TEXT_COLOR
                )
            )
        self.surfaces = []
        for txt, color in texts:
            self.surfaces.append(fonts.big().render(txt, True, color))

    def draw(self, screen, cur_time, dt):
        """
        Draws the 50:50 screen on the given screen.
        """
        if cur_time - self.start_time > 4:
            raise BackToQuestionException()
        self.draw_surfaces_v(screen, HEIGHT // 4, self.surfaces)

    def handle_event(self, event):
        """
        Handles the given event.
        """


class PhonePage(Page):
    """
    Represents the screen displayed when the player uses the phone-a-friend
    lifeline.
    """
    def __init__(self, question):
        """
        Initializes the PhonePage object with the given question.
        """
        super().__init__()
        self.question = question
        self.start_time = time()
        texts = [
            ("Vous avez utilisé le téléphone", ANSWER_SELECTION_COLOR),
            ("Votre ami•e vous a dit :", DEFAULT_TEXT_COLOR),
        ]
        idx, v = question.phone
        if question.is_right_answer(idx):
            texts.append(
                ("Je pense que la réponse est :", DEFAULT_TEXT_COLOR)
            )
        else:
            texts.append(
                ("Je ne suis pas sur, mais :", DEFAULT_TEXT_COLOR)
            )
        texts.append((f"{chr(ord('A')+idx)} à {v}%", DEFAULT_TEXT_COLOR))

        self.surfaces = []
        for txt, color in texts:
            self.surfaces.append(fonts.big().render(txt, True, color))

    def draw(self, screen, cur_time, dt):
        """
        Draws the phone-a-friend screen on the given screen.
        """
        if cur_time - self.start_time > 5:
            raise BackToQuestionException()
        self.draw_surfaces_v(screen, HEIGHT // 4, self.surfaces)

    def handle_event(self, event):
        """
        Handles the given event.
        """


class PublicPage(Page):
    """
    Represents the screen displayed when the player uses the ask-the-audience
    lifeline.
    """
    def __init__(self, question):
        """
        Initializes the PublicPage object with the given question.
        """
        super().__init__()
        self.question = question
        self.start_time = time()
        texts = [
            ("Vous avez utilisé le vote du public.", ANSWER_SELECTION_COLOR),
            ("Voici les résultats :", DEFAULT_TEXT_COLOR),
        ]
        self.surfaces = []
        for txt, color in texts:
            self.surfaces.append(fonts.big().render(txt, True, color))

        self.answers = []
        self.answer_height = 0
        for i, txt in enumerate(self.question.answers):
            surf = fonts.render_text_at_best(
                fonts.big(),
                f"{chr(ord('A')+i)} : {txt}",
                DEFAULT_TEXT_COLOR,
                WIDTH // 2, HEIGHT
            )
            self.answers.append(
                (
                    self.question.public[i] / 100 * WIDTH / 2,
                    surf
                )
            )
            self.answer_height = max(self.answer_height, surf.get_height())

    def draw(self, screen, cur_time, dt):
        """
        Draws the ask-the-audience screen on the given screen.
        """
        if cur_time - self.start_time > 8:
            raise BackToQuestionException()

        y_start = self.draw_surfaces_v(screen, HEIGHT // 4, self.surfaces)

        y_start += 20
        for i, (value, surface) in enumerate(self.answers):
            screen.blit(
                surface,
                (
                    WIDTH // 2 - surface.get_width(),
                    y_start
                )
            )

            pygame.draw.rect(
                screen,
                DEFAULT_TEXT_COLOR,
                (
                    WIDTH // 2 + 10,
                    y_start,
                    int(ease_out(
                        0,
                        value,
                        clamp((cur_time - self.start_time) / 3 - i / 4, 0, 1)
                    )),
                    self.answer_height
                )
            )
            y_start += self.answer_height + 20

    def handle_event(self, event):
        """
        Handles the given event.
        """
