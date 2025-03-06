#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sparkles.py

This module contains the Sparkles class, which simulates a collection
of sparkles moving across a screen with optional gravity effects.

Classes:
    Sparkles: A class to manage and draw sparkles on a screen.

Constants:
    WIDTH: The width of the screen.
    HEIGHT: The height of the screen.
    SPARKLE_COUNT: The default number of sparkles.
"""


import numpy

from config import WIDTH, HEIGHT, SPARKLE_COUNT


# pylint: disable=too-many-instance-attributes
class Sparkles:
    """
    A class to manage and draw sparkles on a screen.
    """
    __slots__ = (
        "rng", "count", "surfs", "surf_len",
        "xs", "ys", "dxs", "dys",
        "age", "life_dt", "gravity"
    )

    def __init__(self, surfs, count=SPARKLE_COUNT, gravity=False):
        """
        Initializes the Sparkles object with the given surfaces and count.
        """
        self.rng = numpy.random.default_rng(128)

        self.count = count
        self.gravity = gravity

        self.surfs = surfs
        self.surf_len = len(surfs)

        self.reset()

    def reset(self):
        """
        Resets the sparkles to their initial state.
        """
        self.xs = self.rng.random(self.count) * WIDTH
        self.ys = self.rng.random(self.count) * WIDTH
        self.age = self.rng.random(self.count)

        self.dxs = 0.001 * (0.5 - self.rng.random(self.count))
        if self.gravity:
            self.dys = 0.001 * (0.5 + numpy.full(self.count, 0.5))
        else:
            self.dys = 0.001 * (0.5 - self.rng.random(self.count))
        self.life_dt = 0.001 * self.rng.random(self.count)

    def get_count(self):
        """
        Returns the number of sparkles.
        """
        return self.count

    def draw(self, screen, dt):
        """
        Draws the sparkles on the given screen.
        """
        self.xs = (self.xs + self.dxs * dt) % WIDTH
        self.ys = (self.ys + self.dys * dt) % HEIGHT
        self.age += self.life_dt * dt

        self.dxs += 0.01 * (0.5 - self.rng.random(self.count))
        self.dys += 0.01 * (0.5 - self.rng.random(self.count))

        surf_idx = numpy.int8(numpy.sin(self.age) * self.surf_len)
        for i in range(self.count):
            # pylint: disable=unsubscriptable-object
            screen.blit(
                self.surfs[surf_idx[i]],
                (int(self.xs[i]), int(self.ys[i]))
            )
