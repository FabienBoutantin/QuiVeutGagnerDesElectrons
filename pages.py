#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines various Page classes for a quiz game using the Pygame
library.
Each Page class represents a different state or screen in the game, such as
the question screen,
startup screen, good answer screen, bad answer screen, victory screen, and
various lifeline screens.

Classes:
    Page: Abstract base class for all pages.
    QuestionPage: Represents the page where the question and answers are
                  displayed.
    StartUpPage: Represents the startup screen of the game.
    GoodAnswerPage: Represents the screen displayed when the player selects
                    the correct answer.
    BadAnswerPage: Represents the screen displayed when the player selects the
                   wrong answer.
    VictoryPage: Represents the screen displayed when the player wins the game.
    FiftyPage: Represents the screen displayed when the player uses the 50:50
               lifeline.
    PhonePage: Represents the screen displayed when the player uses the
               phone-a-friend lifeline.
    PublicPage: Represents the screen displayed when the player uses the
                ask-the-audience lifeline.

Functions:
    draw_cartouche: Draws a cartouche (decorative frame) around a given
    rectangle on the screen.
"""


from abc import ABC, abstractmethod
from pathlib import Path
from time import time
import pygame

from config import WIDTH, HEIGHT, QUESTION_HEIGHT, QUESTION_SPAN, \
                   ANSWER_HEIGHT, ANSWER_SPAN, \
                   ANSWER_LINE_COLOR, QUESTION_TEXT_COLOR, \
                   ANSWER_SELECTION_COLOR, ANSWER_BACKGROUND_COLOR, \
                   DEFAULT_TEXT_COLOR, GOOD_TEXT_COLOR, BAD_TEXT_COLOR, \
                   REWARDS
from fonts import fonts
from sparkles import Sparkles
from utils import BackToQuestionException, StartupException
from utils import ease_out, clamp, get_logo_surf


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


class Page(ABC):
    """
    Abstract base class for all pages in the game.
    """
    @abstractmethod
    def draw(self, screen, cur_time, dt):
        """
        Draws the page on the screen.
        """

    def update(self, cur_time, dt):
        """
        Updates the page state.
        """

    @abstractmethod
    def handle_event(self, event):
        """
        Handles the given event.
        """


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
        self.current_question_idx = None
        self.logo_surface = get_logo_surf()
        self.logo_pos_x = (WIDTH - self.logo_surface.get_size()[0]) // 2
        self.logo_pos_y = HEIGHT // 2 - self.logo_surface.get_size()[1]
        self.logo_pos_y //= 2
        self.logo_pos_y -= 20
        self.question_txt_surf = None
        self.proposition_surfs = [None, None, None, None]

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

    def update_question(self):
        """
        Updates the current question and its text.
        """
        question = self.question_list.get_current_question()
        self.current_question_idx = self.question_list.current_question_idx()

        self.question_txt_surf = fonts.render_text_at_best(
            fonts.normal(),
            question.text,
            QUESTION_TEXT_COLOR,
            QUESTION_RECT.width - 2 * QUESTION_SPAN, QUESTION_RECT.height
        )

        self.proposition_surfs = [None, None, None, None]

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
        self.question_logo_x = (WIDTH - self.logo_surface.get_size()[0]) // 2
        self.question_logo_y = HEIGHT // 2 - self.logo_surface.get_size()[1]
        self.question_logo_y //= 2
        self.question_logo_y -= 20
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
            title_offset_x = (WIDTH - self.title_surface.get_width()) // 2
            src_y = -2 * self.title_surface.get_height()
            target_y = ((HEIGHT // 2 - self.title_surface.get_height()) // 2)
            factor = clamp((cur_time - self.start_time) / 2, 0, 1)
            title_offset_y = ease_out(
                src_y, target_y,
                factor
            )
            screen.blit(
                self.title_surface,
                (title_offset_x, int(title_offset_y))
            )

        src_x = - self.logo_surface.get_width()
        target_x = self.question_logo_x
        src_y = HEIGHT * 0.7 - self.logo_surface.get_height() * 0.5
        target_y = self.question_logo_y
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
        if self.animate_to_question:
            return
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.animate_to_question = True
            self.start_time = time()


# pylint: disable=too-many-instance-attributes
class GoodAnswerPage(Page):
    """
    Represents the screen displayed when the player selects the correct answer.
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(
            self, question, answer,
            text="Bonne réponse !", color=(100, 150, 10),
            exception=BackToQuestionException,
            time_to_wait=4
    ):
        """
        Initializes the GoodAnswerPage object with the given question, answer,
        text, color, exception, and time to wait.
        """
        super().__init__()
        self.text = text
        self.color = color
        self.question = question
        self.answer = question.answers[answer]
        self.exception = exception
        self.time_to_wait = time_to_wait
        self.start_time = time()
        pygame.mouse.set_visible(False)
        self.title_surface = None
        self.question_surface = None
        self.answer_surface = None

    def draw(self, screen, cur_time, dt):
        """
        Draws the good answer screen on the given screen.
        """
        if cur_time - self.start_time > self.time_to_wait:
            pygame.mouse.set_visible(True)
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
            raise self.exception()

        if self.title_surface is None:
            self.title_surface = fonts.big().render(
                self.text, True, self.color
            )
            self.question_surface = fonts.normal().render(
                self.question.text, True, QUESTION_TEXT_COLOR
            )
            self.answer_surface = fonts.normal().render(
                self.answer, True, ANSWER_LINE_COLOR
            )

        title_offset_x = (WIDTH - self.title_surface.get_size()[0]) // 2
        src_y = -2 * self.title_surface.get_height()
        target_y = ((HEIGHT // 2 - self.title_surface.get_height()) // 2)
        factor = clamp((cur_time - self.start_time) / 2, 0, 1)
        title_offset_y = ease_out(
            src_y, target_y,
            factor
        )
        screen.blit(self.title_surface, (title_offset_x, int(title_offset_y)))

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

    def draw_rewards(self, screen):
        """
        Draws the rewards on the given screen.
        """
        y_start = int(HEIGHT * 0.9)
        for i, (step, reward) in enumerate(REWARDS):
            if step:
                color = ANSWER_SELECTION_COLOR
            else:
                color = DEFAULT_TEXT_COLOR
            surface = fonts.small().render(reward, True, color)
            screen.blit(
                surface,
                (
                    10,
                    y_start
                )
            )
            if i == self.question.idx:
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        0,
                        y_start - 2,
                        surface.get_width() + 20,
                        surface.get_height() + 4
                    ),
                    2
                )
            y_start -= surface.get_height() + 10

    def handle_event(self, event):
        """
        Handles the given event.
        """
        go_back = \
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE \
            or \
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 3
        if go_back:
            pygame.mouse.set_visible(True)
            pygame.mouse.set_pos((WIDTH // 2, HEIGHT // 2))
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
            good_answer = self.question.answers[self.question.correct_answer]
            good_answer_surface = fonts.normal().render(
                good_answer, True, GOOD_TEXT_COLOR
            )
            screen.blit(
                good_answer_surface,
                (
                    WIDTH // 2 - good_answer_surface.get_width() // 2,
                    int(HEIGHT / 2 + self.answer_surface.get_height() * 1.5)
                )
            )


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
        self.texts = (
            ("Bravo ! Vous avez gagné !", GOOD_TEXT_COLOR),
            ("Vous pouvez maintenant participer", DEFAULT_TEXT_COLOR),
            ("à ce projet de quartier !", DEFAULT_TEXT_COLOR),
            ("", (0, 0, 0)),
            ("Plus d'informations sur :", ANSWER_SELECTION_COLOR),
            ("https://www.clairvolt.fr", ANSWER_SELECTION_COLOR),
        )

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
        for txt, color in self.texts:
            surface = fonts.big().render(txt, True, color)
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
        self.texts = [
            ("Vous avez utilisé le 50:50", ANSWER_SELECTION_COLOR),
            ("Vous avez maintenant le choix", DEFAULT_TEXT_COLOR),
            ("entre les deux réponses suivantes", DEFAULT_TEXT_COLOR),
        ]
        for i in question.fifty_fifty:
            self.texts.append(
                (
                    f'{chr(ord("A") + i)} : {question.answers[i]}',
                    DEFAULT_TEXT_COLOR
                )
            )

    def draw(self, screen, cur_time, dt):
        """
        Draws the 50:50 screen on the given screen.
        """
        if cur_time - self.start_time > 4:
            raise BackToQuestionException()

        y_start = HEIGHT // 4
        for txt, color in self.texts:
            surface = fonts.big().render(txt, True, color)
            screen.blit(
                surface,
                (
                    (WIDTH - surface.get_width()) // 2,
                    y_start
                )
            )
            y_start += surface.get_height() + 20

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
        self.texts = [
            ("Vous avez utilisé le téléphone", ANSWER_SELECTION_COLOR),
            ("Votre ami•e vous a dit :", DEFAULT_TEXT_COLOR),
        ]
        idx, v = question.phone
        if question.is_right_answer(idx):
            self.texts.append(
                ("Je pense que la réponse est :", DEFAULT_TEXT_COLOR)
            )
        else:
            self.texts.append(
                ("Je ne suis pas sur, mais :", DEFAULT_TEXT_COLOR)
            )
        self.texts.append((f"{chr(ord('A')+idx)} à {v}%", DEFAULT_TEXT_COLOR))

    def draw(self, screen, cur_time, dt):
        """
        Draws the phone-a-friend screen on the given screen.
        """
        if cur_time - self.start_time > 5:
            raise BackToQuestionException()

        y_start = HEIGHT // 4
        for txt, color in self.texts:
            surface = fonts.big().render(txt, True, color)
            screen.blit(
                surface,
                (
                    (WIDTH - surface.get_width()) // 2,
                    y_start
                )
            )
            y_start += surface.get_height() + 20

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
        self.texts = [
            ("Vous avez utilisé le vote du public.", ANSWER_SELECTION_COLOR),
            ("Voici les résultats :", DEFAULT_TEXT_COLOR),
        ]

    def draw(self, screen, cur_time, dt):
        """
        Draws the ask-the-audience screen on the given screen.
        """
        if cur_time - self.start_time > 8:
            raise BackToQuestionException()

        y_start = HEIGHT // 4
        for txt, color in self.texts:
            surface = fonts.big().render(txt, True, color)
            screen.blit(
                surface,
                (
                    (WIDTH - surface.get_width()) // 2,
                    y_start
                )
            )
            y_start += surface.get_height() + 10

        y_start += 20
        for i, txt in enumerate(self.question.answers):
            surface = fonts.big().render(
                f"{chr(ord('A')+i)} : {txt}",
                True,
                DEFAULT_TEXT_COLOR
            )
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
                        self.question.public[i] / 100 * WIDTH / 2,
                        clamp((cur_time - self.start_time) / 3 - i / 4, 0, 1)
                    )),
                    surface.get_height()
                )
            )
            y_start += surface.get_height() + 20

    def handle_event(self, event):
        """
        Handles the given event.
        """
