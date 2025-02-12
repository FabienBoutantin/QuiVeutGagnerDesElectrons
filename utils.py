#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame


__LOGO_SURF = None


def interp_value(a, b, factor):
    return a + (b - a) * factor


def ease_in(a, b, factor):
    return a + (b - a) * factor * factor


def ease_out(a, b, factor):
    return b + (a - b) * (1 - factor) * (1 - factor)


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def interp_color(col1, col2, factor):
    return tuple(int(interp_value(col1[i], col2[i], factor)) for i in range(3))


def gradient_rect(screen, colors, target_rect):
    """ Draw a horizontal-gradient filled rectangle covering <target_rect> """
    # tiny! 2x2 bitmap
    colour_rect = pygame.Surface((2, 2))
    for i in range(4):
        raw = i // 2
        col = i % 2
        colour_rect.set_at((col, raw), colors[i])

    colour_rect = pygame.transform.smoothscale(
        colour_rect,
        (target_rect.width, target_rect.height)
    )  # stretch to fit new rect!
    screen.blit(colour_rect, target_rect)


def get_logo_surf():
    global __LOGO_SURF
    if __LOGO_SURF is None:
        __LOGO_SURF = pygame.image.load("assets/logo.png")
    return __LOGO_SURF


class GameException(Exception):
    __slots__ = ("question", "answer")

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


class GoodAnswerException(GameException):
    pass


class BadAnswerException(GameException):
    pass


class VictoryException(Exception):
    pass


class BackToQuestionException(Exception):
    pass


class FiftyException(GameException):
    pass


class PhoneException(GameException):
    pass


class PublicException(GameException):
    pass


class StartupException(Exception):
    pass
