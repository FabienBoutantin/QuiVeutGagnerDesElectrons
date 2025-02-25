#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fonts.py

This module provides a Fonts class to manage different font sizes and render
text with pygame.

Classes:
    Fonts: A class to initialize and manage different font sizes and render
           text.

Usage:
    fonts.init()
    big_font = fonts.big()
    normal_font = fonts.normal()
    small_font = fonts.small()
    rendered_text = fonts.render_text_at_best(font, text, color, width, height)
"""


import pygame

from config import FONT_BIG, FONT_NORMAL, FONT_SMALL


class Fonts:
    """
    A class to initialize and manage different font sizes and render text.
    """
    def __init__(self):
        """ Default constuctor."""
        self._font_big = None
        self._font_normal = None
        self._font_small = None

    def init(self):
        """ Initialize the fonts."""
        self._font_big = pygame.font.SysFont("Arial", FONT_BIG)
        self._font_normal = pygame.font.SysFont("Arial", FONT_NORMAL)
        self._font_small = pygame.font.SysFont("Arial", FONT_SMALL)

    def big(self):
        """ Get the big font."""
        return self._font_big

    def normal(self):
        """ Get the normal font."""
        return self._font_normal

    def small(self):
        """ Get the small font."""
        return self._font_small

    # pylint: disable=too-many-positional-arguments
    def render_text_at_best(self, font, text, color, width, height):
        """
        Render text with the given font, color, and size, scaling it to fit
        within the given width and height.
        """
        w, h = font.size(text)
        ratio = w/h
        if w > width:
            size = (width, int(width / ratio))
        elif h > height:
            size = (int(height * ratio), height)
        else:
            return font.render(text, False, color)
        return pygame.transform.smoothscale(
            font.render(text, False, color).convert_alpha(),
            size
        )


fonts = Fonts()
