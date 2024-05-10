import arcade
import math

import config
from typing import List
from pyglet.math import Vec2
from dataclasses import dataclass, field


@dataclass
class Planet:
    x: float = 0
    y: float = 0
    r: int = 1
    mass: int = 1
    speed: Vec2 = None


class PhysicsEngine:
    def __init__(self, planets: List[Planet]):
        self.planets = planets

    def update(self, dt: float):
        removed: List[bool] = [False for i in range(len(self.planets))]
        for i in range(len(self.planets)):
            for j in range(i):
                dist = ((self.planets[i].x - self.planets[j].x) ** 2 + (
                        self.planets[i].y - self.planets[j].y) ** 2)
                if dist <= (self.planets[i].r + self.planets[j].r) ** 2:
                    if self.planets[i].mass < self.planets[j].mass:
                        self.planets[i], self.planets[j] = self.planets[j], self.planets[i]

                    removed[j] = True
                    summ = (self.planets[i].mass + self.planets[j].mass)
                    self.planets[i].speed = (self.planets[i].speed * Vec2(self.planets[i].mass,
                                                                          self.planets[i].mass) +
                                             self.planets[j].speed * Vec2(self.planets[j].mass,
                                                                          self.planets[j].mass)) / Vec2(summ, summ)
                    self.planets[i].mass = summ
                    self.planets[i].r = (self.planets[i].mass / 3) ** (1/3)

        planets = []
        for i in range(len(self.planets)):
            if not removed[i]:
                planets.append(self.planets[i])
        self.planets = planets

        forces: List[Vec2] = [Vec2(0, 0) for i in range(len(self.planets))]

        for i in range(len(self.planets)):
            for j in range(i):
                dist = ((self.planets[i].x - self.planets[j].x) ** 2 + (
                        self.planets[i].y - self.planets[j].y) ** 2)

                force = config.GRAVITY_CONST * (self.planets[i].mass * self.planets[j].mass / dist)
                angle = math.atan2(self.planets[i].y - self.planets[j].y, self.planets[i].x - self.planets[j].x)
                forces[i].x -= force * math.cos(angle)
                forces[i].y -= force * math.sin(angle)
                forces[j].x += force * math.cos(angle)
                forces[j].y += force * math.sin(angle)

        for i in range(len(self.planets)):
            self.planets[i].speed.x += forces[i].x * config.TIMESTEP / self.planets[i].mass
            self.planets[i].speed.y += forces[i].y * config.TIMESTEP / self.planets[i].mass

        for i in range(len(self.planets)):
            self.planets[i].x += self.planets[i].speed.x * dt
            self.planets[i].y += self.planets[i].speed.y * dt
