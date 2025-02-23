#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module defines base Page classes for a quiz game using the Pygame
library.
Each Page class represents a different state or screen in the game, such as
the question screen,
startup screen, good answer screen, bad answer screen, victory screen, and
various lifeline screens.

Classes:
    Page: Abstract base class for all pages.
"""


from abc import ABC, abstractmethod
from pygame import Surface

from config import WIDTH, HEIGHT
from utils import ease_out, clamp


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

    def animate_surf_v(self, screen, surf, cur_time, start_time, duration):
        """
        Animates the given surface vertically on the screen.
        """
        x = (WIDTH - surf.get_size()[0]) // 2
        src_y = -2 * surf.get_height()
        target_y = ((HEIGHT // 2 - surf.get_height()) // 2)
        factor = clamp((cur_time - start_time) / duration, 0, 1)
        y = ease_out(src_y, target_y, factor)
        screen.blit(surf, (x, int(y)))

    def draw_surfaces_v(
            self, screen: Surface,
            y_start: int, surfaces: list
    ) -> int:
        """
        Draws the given surfaces vertically on the screen.
        """
        for surface in surfaces:
            screen.blit(
                surface,
                (
                    (WIDTH - surface.get_width()) // 2,
                    y_start
                )
            )
            y_start += surface.get_height() + 20
        return y_start
