#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy

from config import WIDTH, HEIGHT, SPARKLE_COUNT


class Sparkles:
    __slots__ = (
        "rng", "count", "surfs", "surf_len",
        "xs", "ys", "dxs", "dys",
        "age", "life_dt"
    )

    def __init__(self, surfs, count=SPARKLE_COUNT, gravity=False):
        self.rng = numpy.random.default_rng(128)

        self.count = count

        self.surfs = surfs
        self.surf_len = len(surfs)

        self.xs = self.rng.random(count) * WIDTH
        self.ys = self.rng.random(count) * WIDTH
        self.age = self.rng.random(count)

        self.dxs = 0.5 - self.rng.random(count)
        if gravity:
            self.dys = 0.5 + numpy.full(count, 0.5)
        else:
            self.dys = 0.5 - self.rng.random(count)
        self.life_dt = numpy.full(count, 0.01)

    def draw(self, screen):
        self.xs = (self.xs + self.dxs) % WIDTH
        self.ys = (self.ys + self.dys) % HEIGHT
        self.age += self.life_dt

        self.dxs += 0.01 * (0.5 - self.rng.random(self.count))
        self.dys += 0.01 * (0.5 - self.rng.random(self.count))
        self.life_dt += 0.001 * (0.5 - self.rng.random(self.count))

        surf_idx = numpy.int8(numpy.sin(self.age) * self.surf_len)
        for i in range(self.count):
            screen.blit(
                self.surfs[surf_idx[i]],
                (int(self.xs[i]), int(self.ys[i]))
            )
