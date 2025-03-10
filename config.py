#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for the 'QuiVeutGagnerDesElectrons' game.

This module contains various constants used throughout the game, such as
colors, dimensions, and reward tiers.

Constants:
    BACKGROUND_COLOR (tuple): RGB color for the primary background.
    BACKGROUND_COLOR2 (tuple): RGB color for the secondary background.
    SPARKLE_COUNT (int): Number of sparkles to display.
    WIDTH (int): Width of the game window.
    HEIGHT (int): Height of the game window.
    REWARDS (tuple): Tuple of reward tiers, each containing a boolean
                     indicating if it's a milestone and the reward description.
    QUESTION_HEIGHT (int): Height of the question area.
    QUESTION_SPAN (int): Vertical span between questions.
    QUESTION_TEXT_COLOR (tuple): RGB color for the question text.
    ANSWER_HEIGHT (int): Height of the answer area.
    ANSWER_SPAN (int): Vertical span between answers.
    ANSWER_LINE_COLOR (tuple): RGB color for the answer lines.
"""


BACKGROUND_COLOR = (30, 32, 64)
BACKGROUND_COLOR2 = (64, 32, 40)
SPARKLE_COUNT = 10

WIDTH = 1366
HEIGHT = 768

FONT_BIG = int(54 / 768 * HEIGHT)
FONT_NORMAL = int(48 / 768 * HEIGHT)
FONT_SMALL = int(32 / 768 * HEIGHT)

QUESTION_HEIGHT = HEIGHT // 8
QUESTION_SPAN = QUESTION_HEIGHT // 2
QUESTION_TEXT_COLOR = (255, 255, 0)
QUESTION_COUNT = 6
RANDOMIZE_CHOICES = False

ANSWER_HEIGHT = HEIGHT // 10
ANSWER_SPAN = ANSWER_HEIGHT // 2
ANSWER_LINE_COLOR = (200, 200, 200)
ANSWER_SELECTION_COLOR = (200, 200, 0)
ANSWER_BACKGROUND_COLOR = (55, 25, 55)

DEFAULT_TEXT_COLOR = (200, 200, 200)
GOOD_TEXT_COLOR = (0, 255, 0)
BAD_TEXT_COLOR = (255, 0, 0)

REWARDS = (
    (False, "500 Wh"),
    (True, "1500 Wh"),  # Palier 1
    (False, "3 kWh"),
    (False, "6 kWh"),
    (False, "12 kWh"),
    (False, "24 kWh"),
    (True, "48 kWh"),  # Palier 2
    (False, "72 kWh"),
    (False, "100 kWh"),
    (False, "150 kWh"),
    (False, "300 kWh"),
    (True, "1 MWh"),  # Palier 3
)
