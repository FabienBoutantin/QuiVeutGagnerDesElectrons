#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines the main Page classes for a quiz game using the Pygame
library: the question Page.

Classes:
    QuestionPage: Represents the page where the question and answers are
                  displayed.

Functions:
    draw_cartouche: Draws a cartouche (decorative frame) around a given
    rectangle on the screen.
"""


import pygame

from config import WIDTH, HEIGHT, QUESTION_HEIGHT, QUESTION_SPAN, \
                   ANSWER_HEIGHT, ANSWER_SPAN, \
                   ANSWER_LINE_COLOR, QUESTION_TEXT_COLOR, \
                   ANSWER_SELECTION_COLOR, ANSWER_BACKGROUND_COLOR, \
                   DEFAULT_TEXT_COLOR, BAD_TEXT_COLOR
from fonts import fonts
from pages.base_page import Page
from utils import get_logo_surf


# Top, left, width, height
QUESTION_RECT = pygame.Rect(
    (QUESTION_SPAN, HEIGHT // 2 - QUESTION_HEIGHT // 2),
    (WIDTH - QUESTION_SPAN * 2, QUESTION_HEIGHT)
)


def get_answer_rect_list() -> list:
    """
    Returns a list of pygame.Rect objects representing the answer rectangles.
    """
    result = []
    for y in range(2):
        for x in range(2):
            left = x * (WIDTH // 2) + ANSWER_SPAN
            top = HEIGHT // 2 + QUESTION_HEIGHT + y * ANSWER_HEIGHT
            top += y * ANSWER_SPAN // 2
            width = WIDTH // 2 - ANSWER_SPAN * 2
            height = HEIGHT // 4 - ANSWER_HEIGHT
            result.append(pygame.Rect(left, top, width, height))
    return result


ANSWER_RECTS = get_answer_rect_list()

ANSWER_KEYS = (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d)


def draw_cartouche(screen, rect, span, selection=False):
    """
    Draws a cartouche (decorative frame) around a given rectangle on
    the given screen.
    """
    if selection:
        back_color = ANSWER_SELECTION_COLOR
    else:
        back_color = ANSWER_BACKGROUND_COLOR
    # Main rect
    pygame.draw.rect(screen, back_color, rect, 0, span)
    pygame.draw.rect(screen, ANSWER_LINE_COLOR, rect, 4, span)

    # Left lines
    pygame.draw.rect(
        screen,
        ANSWER_LINE_COLOR,
        (rect.left - span, rect.centery - 10, span, 20),
        4
    )
    pygame.draw.rect(
        screen,
        back_color,
        (rect.left - span, rect.centery - 10 + 4, span + 4, 20 - 2 * 4),
        0
    )

    # Right lines
    pygame.draw.rect(
        screen,
        ANSWER_LINE_COLOR,
        (rect.right, rect.centery - 10, span, 20),
        4
    )
    pygame.draw.rect(
        screen,
        back_color,
        (rect.right - 4, rect.centery - 10 + 4, span + 4, 20 - 2 * 4),
        0
    )


# pylint: disable=too-many-instance-attributes
class QuestionPage(Page):
    """
    Represents the page where the question and answers are displayed.
    """
    def __init__(self, question_list):
        """
        Initializes the QuestionPage object with the given question list.
        """
        super().__init__()
        self.question_list = question_list
        self.current_question_idx = self.question_list.current_question_idx()
        self.logo_surface = get_logo_surf()
        self.logo_pos_x = (WIDTH - self.logo_surface.get_size()[0]) // 2
        self.logo_pos_y = HEIGHT // 2 - self.logo_surface.get_size()[1]
        self.logo_pos_y //= 2
        self.logo_pos_y -= 20

        question = self.question_list.get_current_question()

        self.question_txt_surf = fonts.render_text_at_best(
            fonts.normal(),
            question.text,
            QUESTION_TEXT_COLOR,
            QUESTION_RECT.width - 2 * QUESTION_SPAN, QUESTION_RECT.height
        )

        self.buttons = []
        # 50:50 button
        action = self.question_list.use_fifty
        used = self.question_list.is_fifty_used
        txt = fonts.normal().render("50 %", True, ANSWER_SELECTION_COLOR)
        rect = pygame.Rect(
            WIDTH - txt.get_width() - txt.get_height() * 2,
            0,
            txt.get_width() + txt.get_height() * 2,
            txt.get_height() + 10
        )
        rect.move_ip(0, 10)
        self.buttons.append((txt, rect, action, used))

        # phone call button
        used = self.question_list.is_phone_used
        action = self.question_list.use_phone
        txt = fonts.normal().render("\u2706", True, ANSWER_SELECTION_COLOR)
        rect = pygame.Rect(
            WIDTH - txt.get_width() - txt.get_height() * 2,
            4,
            txt.get_width() + txt.get_height() * 2,
            txt.get_height() + 10
        )
        rect.move_ip(0, rect.height + 10 + 10)
        self.buttons.append((txt, rect, action, used))

        # the Public button ("\U0001F5EB" was good but is unknown)
        used = self.question_list.is_public_used
        action = self.question_list.use_public
        txt = fonts.normal().render("Vote", True, ANSWER_SELECTION_COLOR)
        rect = pygame.Rect(
            WIDTH - txt.get_width() - txt.get_height() * 2,
            4,
            txt.get_width() + txt.get_height() * 2,
            txt.get_height() + 10
        )
        rect.move_ip(0, 2 * (rect.height + 10) + 10)
        self.buttons.append((txt, rect, action, used))

    def handle_event(self, event):
        """
        Handles the given event.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in ANSWER_KEYS:
                answer = ANSWER_KEYS.index(event.key)
                self.question_list.validate_answer(answer)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i in range(4):
                if ANSWER_RECTS[i].collidepoint(mouse_pos):
                    self.question_list.validate_answer(i)
            for _, rect, action, used in self.buttons:
                if not used() and rect.collidepoint(mouse_pos):
                    action()

    def draw(self, screen, cur_time, dt):
        """
        Draws the question and answers on the screen.
        """
        question = self.question_list.get_current_question()

        screen.blit(
            self.logo_surface, (self.logo_pos_x, self.logo_pos_y)
        )

        self.draw_question(screen)

        for i, answer in enumerate(question.answers):
            self.draw_proposition(screen, i, answer, fonts.small())

        for txt, rect, _, used in self.buttons:
            if not used() and rect.collidepoint(pygame.mouse.get_pos()):
                back_color = ANSWER_SELECTION_COLOR
            else:
                back_color = ANSWER_BACKGROUND_COLOR

            span = rect.height // 2
            pygame.draw.rect(screen, back_color, rect, 0, span)
            pygame.draw.rect(screen, ANSWER_LINE_COLOR, rect, 4, span)
            screen.blit(
                txt,
                (
                    rect.centerx - txt.get_width() // 2,
                    rect.centery - txt.get_height() // 2,
                )
            )
            if used():
                pygame.draw.line(
                    screen,
                    BAD_TEXT_COLOR,
                    rect.topleft,
                    rect.bottomright,
                    15
                )

    def draw_question(self, screen):
        """
        Draws the question on the screen.
        """
        draw_cartouche(screen, QUESTION_RECT, QUESTION_SPAN)

        w, h = self.question_txt_surf.get_size()
        screen.blit(
            self.question_txt_surf,
            (
                QUESTION_RECT.centerx - w // 2,
                QUESTION_RECT.centery - h // 2
            )
        )

    def draw_proposition(self, screen, i, text, font):
        """
        Draws the given proposition on the screen.
        """
        is_selected = ANSWER_RECTS[i].collidepoint(pygame.mouse.get_pos())
        draw_cartouche(
            screen,
            ANSWER_RECTS[i], ANSWER_SPAN,
            selection=is_selected
        )

        if is_selected:
            txt_color = (0, 0, 255)
        else:
            txt_color = DEFAULT_TEXT_COLOR
        answer_txt = font.render(
            f'{chr(ord("A")+i)} : ', True, QUESTION_TEXT_COLOR
        )
        x = ANSWER_RECTS[i].left + ANSWER_HEIGHT // 2
        y = ANSWER_RECTS[i].centery - answer_txt.get_height() // 2
        screen.blit(answer_txt, (x, y))
        x += answer_txt.get_width()
        answer_txt = font.render(text, True, txt_color)
        screen.blit(answer_txt, (x, y))
