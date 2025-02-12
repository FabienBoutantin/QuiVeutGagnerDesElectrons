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


class Fonts:
    def __init__(self):
        # This is intentionally empty
        pass

    def init(self):
        self._font_big = pygame.font.SysFont("Arial", 54)
        self._font_normal = pygame.font.SysFont("Arial", 48)
        self._font_small = pygame.font.SysFont("Arial", 32)

    def big(self):
        return self._font_big

    def normal(self):
        return self._font_normal

    def small(self):
        return self._font_small

    def render_text_at_best(self, font, text, color, width, height):
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
