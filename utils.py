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


def interp_value(a: float, b: float, factor: float) -> float:
    """ Interpolates between two values a and b by a given factor. """
    return a + (b - a) * factor


def ease_in(a: float, b: float, factor: float) -> float:
    """
        Applies an ease-in interpolation between two values a and b
        by a given factor.
    """
    return a + (b - a) * factor * factor


def ease_out(a: float, b: float, factor: float) -> float:
    """
        Applies an ease-out interpolation between two values a and b
        by a given factor.
    """
    return b + (a - b) * (1 - factor) * (1 - factor)


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
        Clamps a value between a minimum and maximum value.
    """
    return max(min(value, max_value), min_value)


def interp_color(col1: tuple, col2: tuple, factor: float) -> tuple:
    """
        Interpolates between two colors by a given factor.
    """
    return tuple(int(interp_value(col1[i], col2[i], factor)) for i in range(3))


def gradient_rect(
        screen: pygame.Surface,
        colors: tuple,
        target_rect: pygame.Rect
        ) -> None:
    """
        Draw a 4 corners gradient filled rectangle covering <target_rect>
        with the gradient defined by <colors>.
    """
    # tiny! 2x2 bitmap
    colour_rect = pygame.Surface((2, 2))
    for i in range(4):
        raw = i // 2
        col = i % 2
        colour_rect.set_at((col, raw), colors[i])

    colour_rect = pygame.transform.smoothscale(
        colour_rect,
        target_rect.size,
        screen
    )  # stretch to fit new rect!


def get_logo_surf() -> pygame.Surface:
    """
        Loads and returns the logo surface from the assets.
    """
    global __LOGO_SURF
    if __LOGO_SURF is None:
        __LOGO_SURF = pygame.image.load("assets/logo.png").convert_alpha()
    return __LOGO_SURF


class GameException(Exception):
    """
        Base class for game-related exceptions.
    """
    __slots__ = ("question", "answer")

    def __init__(self, question, answer):
        """ Base constructor for game-related exceptions. """
        self.question = question
        self.answer = answer


class GoodAnswerException(GameException):
    """
        Exception raised for a correct answer.
    """


class BadAnswerException(GameException):
    """
        Exception raised for an incorrect answer.
    """


class VictoryException(Exception):
    """
        Exception raised for a victory.
    """


class BackToQuestionException(Exception):
    """
        Exception raised to go back to question page.
    """


class FiftyException(GameException):
    """
        Exception raised for the fifty-fifty bonus.
    """


class PhoneException(GameException):
    """
        Exception raised for the phone-a-friend bonus.
    """


class PublicException(GameException):
    """
        Exception raised for the ask-the-audience bonus.
    """


class StartupException(Exception):
    """
        Exception raised to reset the game.
    """
