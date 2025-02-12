#!/usr/bin/env python3
# -*- coding: utf-8 -*-


BACKGROUND_COLOR = (30, 32, 64)
BACKGROUND_COLOR2 = (64, 32, 40)
SPARKLE_COUNT = 30

WIDTH = 1365
HEIGHT = 768

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

QUESTION_HEIGHT = 100
QUESTION_SPAN = 50
QUESTION_TEXT_COLOR = (255, 255, 0)

ANSWER_HEIGHT = 100
ANSWER_SPAN = 40
ANSWER_LINE_COLOR = (200, 200, 200)
