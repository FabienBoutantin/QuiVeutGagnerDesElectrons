#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
utils.py

This module contains utility functions and custom exceptions
for the game "Qui Veut Gagner Des Electrons".

Functions:
    interp_value(a, b, factor):
      Interpolates between two values a and b by a given factor.
    ease_in(a, b, factor):
      Applies an ease-in interpolation between two values
      a and b by a given factor.
    ease_out(a, b, factor):
      Applies an ease-out interpolation between two values
      a and b by a given factor.
    clamp(value, min_value, max_value):
      Clamps a value between a minimum and maximum value.
    interp_color(col1, col2, factor):
      Interpolates between two colors by a given factor.
    gradient_rect(screen, colors, target_rect):
      Draws a horizontal-gradient filled rectangle covering the target_rect.
    get_logo_surf():
      Loads and returns the logo surface from the assets.

Classes:
    GameException: Base class for game-related exceptions.
    GoodAnswerException: Exception raised for a correct answer.
    BadAnswerException: Exception raised for an incorrect answer.
    VictoryException: Exception raised for a victory.
    BackToQuestionException: Exception raised to go back to a question page.
    FiftyException: Exception raised for the fifty-fifty bonus.
    PhoneException: Exception raised for the phone-a-friend bonus.
    PublicException: Exception raised for the ask-the-audience bonus.
    StartupException: Exception raised for startup-related issues.
"""


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
