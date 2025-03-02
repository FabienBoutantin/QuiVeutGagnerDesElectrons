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


ANSWER_KEYS = (pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d)


def draw_cartouche(surface, span, selection=False, line_width=4):
    """
    Draws a cartouche (decorative frame) around a given rectangle on
    the given surface.
    """
    if selection:
        back_color = ANSWER_SELECTION_COLOR
    else:
        back_color = ANSWER_BACKGROUND_COLOR
    w, h = surface.get_size()
    main_rect = pygame.Rect((span, 0), (w - 2*span, h))
    # Main rect
    pygame.draw.rect(surface, back_color, main_rect, 0, span)
    pygame.draw.rect(surface, ANSWER_LINE_COLOR, main_rect, line_width, span)

    thickness = h // 4
    for left in (0, main_rect.right):
        pygame.draw.rect(
            surface,
            ANSWER_LINE_COLOR,
            (
                left,
                main_rect.centery - thickness // 2,
                span,
                thickness
            ),
            line_width
        )
        pygame.draw.rect(
            surface,
            back_color,
            (
                left - line_width,
                main_rect.centery - thickness // 2 + line_width,
                span + 2 * line_width,
                thickness - 2 * line_width
            )
        )
    main_rect.left += span
    main_rect.width -= 2 * span
    return main_rect


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
        self.highlighted = None
        self.question_list = question_list
        self.question = self.question_list.get_current_question()

        self.init_logo()
        self.init_question()
        self.init_lifelines()

        pygame.mouse.set_visible(True)

    def init_logo(self):
        """
        Initializes the logo surface and position.
        """
        self.logo_surface = get_logo_surf()
        x = (WIDTH - self.logo_surface.get_width()) // 2
        y = HEIGHT // 2 - self.logo_surface.get_height()
        y //= 2
        y -= 20
        self.logo_pos = (x, y)

    def init_question(self):
        """
        Initializes the question and answer surfaces.
        """
        self.question_surf = pygame.surface.Surface(
            (WIDTH, QUESTION_HEIGHT), pygame.SRCALPHA
        )
        inner_rect = draw_cartouche(self.question_surf, QUESTION_SPAN)
        question_txt_surf = fonts.render_text_at_best(
            fonts.normal(),
            self.question.text,
            QUESTION_TEXT_COLOR,
            inner_rect.width, inner_rect.height
        )
        w, h = question_txt_surf.get_size()
        self.question_pos = (0, (HEIGHT - QUESTION_HEIGHT) // 2)
        self.question_surf.blit(
            question_txt_surf,
            ((WIDTH - w) // 2, (self.question_surf.get_height() - h) // 2)
        )

        font = fonts.normal()
        self.answer_surfaces = []
        for i in range(4):
            surfaces = []
            for selected in (False, True):
                s = pygame.surface.Surface(
                    (WIDTH // 2, ANSWER_HEIGHT), pygame.SRCALPHA
                )
                inner_rect = draw_cartouche(s, ANSWER_SPAN, selected)
                answer_txt = font.render(
                    f'{chr(ord("A")+i)} : ', True, QUESTION_TEXT_COLOR
                )
                x = inner_rect.left
                y = (inner_rect.height - answer_txt.get_height()) // 2
                s.blit(answer_txt, (x, y))
                x += answer_txt.get_width()
                if selected:
                    txt_color = (0, 0, 255)
                else:
                    txt_color = DEFAULT_TEXT_COLOR
                answer_txt = fonts.render_text_at_best(
                    font,
                    self.question.display_answers[i],
                    txt_color,
                    inner_rect.width - answer_txt.get_width(),
                    inner_rect.height
                )
                y = (inner_rect.height - answer_txt.get_height()) // 2
                s.blit(answer_txt, (x, y))
                surfaces.append(s)

            x = WIDTH // 2 * (i % 2)
            y = self.question_pos[1] + self.question_surf.get_height()
            y += ANSWER_SPAN
            if i > 1:
                y += ANSWER_HEIGHT + ANSWER_SPAN
            rect = pygame.Rect((x, y), (WIDTH // 2, ANSWER_HEIGHT))
            self.answer_surfaces.append((surfaces, rect))

    def init_lifelines(self):
        """
        Initializes the lifeline buttons.
        """
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
        # Unfortunately the phone emoji is not available in the font
        # "\u2706" was good but is unknown on target system
        txt = fonts.normal().render("Ami", True, ANSWER_SELECTION_COLOR)
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
        txt = fonts.normal().render("Publique", True, ANSWER_SELECTION_COLOR)
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
            self.handle_key(event.key)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_button_down()

    def handle_key(self, key):
        """
        Handles the given key press event.
        """
        try:
            answer = ANSWER_KEYS.index(key)
            self.question_list.validate_answer(answer)
        except ValueError:
            pass

    def handle_mouse_motion(self):
        """
        Handles the mouse motion event.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.highlighted = None
        for i, (_, rect) in enumerate(self.answer_surfaces):
            if rect.collidepoint(mouse_pos):
                self.highlighted = i
                return

    def handle_mouse_button_down(self):
        """
        Handles the mouse button down event.
        """
        mouse_pos = pygame.mouse.get_pos()
        for i, (_, rect) in enumerate(self.answer_surfaces):
            if rect.collidepoint(mouse_pos):
                self.question_list.validate_answer(i)
                return
        for _, rect, action, used in self.buttons:
            if not used() and rect.collidepoint(mouse_pos):
                action()
                return

    def draw(self, screen, cur_time, dt):
        """
        Draws the question and answers on the screen.
        """
        screen.blit(
            self.logo_surface, self.logo_pos
        )

        screen.blit(
            self.question_surf,
            self.question_pos
        )

        for i, (surfs, rect) in enumerate(self.answer_surfaces):
            screen.blit(
                surfs[self.highlighted == i],
                rect.topleft
            )

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
