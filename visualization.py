import arcade
import config
import math
from random import randint
from pyglet.math import Vec2
from typing import Union, List, Callable, Tuple
from simulation import Planet, PhysicsEngine


class Camera:
    def __init__(self, smooth_speed: float):
        self.x: int = 0
        self.y: int = 0

        self.zoom: int = 1
        self.smooth_speed: float = smooth_speed

        self.position_excepted = Vec2(0, 0)
        self.zoom_excepted: float = 1

    def update(self):
        self.x = self.x * (1 - self.smooth_speed) + self.position_excepted.x * self.smooth_speed
        self.y = self.y * (1 - self.smooth_speed) + self.position_excepted.y * self.smooth_speed

        self.zoom = self.zoom * (1 - self.smooth_speed) + self.zoom_excepted * self.smooth_speed


class App(arcade.Window):
    def __init__(self):
        self.gui_camera: Union[arcade.Camera, None] = None
        self.gui_fields: List[Tuple[str, Callable]] = []

        self.camera: Union[Camera, None] = None
        self.physics: Union[PhysicsEngine, None] = None
        super().__init__(config.WIDTH, config.HEIGHT, config.TITLE)

        self.curr_size: int = 1000000
        self.left_pressed: bool = False
        self.right_pressed: bool = False
        self.up_pressed: bool = False
        self.down_pressed: bool = False

        self.creating: bool = False
        self.pos: Vec2 = Vec2(0, 0)
        self.mouse_pos_begin: Vec2 = Vec2(0, 0)
        self.mouse_pos: Vec2 = Vec2(0, 0)

    def setup(self):
        arcade.enable_timings()

        self.gui_fields.append(("X: ", lambda: self.camera.x))
        self.gui_fields.append(("Y: ", lambda: self.camera.y))
        self.gui_fields.append(("Zoom: ", lambda: self.camera.zoom))
        self.gui_fields.append(("Current Size: ", lambda: self.curr_size))
        self.gui_fields.append(("FPS: ", lambda: arcade.get_fps()))
        self.gui_fields.append(("Objects count: ", lambda: len(self.physics.planets)))
        self.gui_fields.append(("Biggest: ", lambda: self.physics.planets[-1].mass))
        self.camera = Camera(0.175)
        self.gui_camera = arcade.Camera(config.WIDTH, config.HEIGHT)

        planets = [
            Planet(
                0, 0, (5 * 10 ** 7 / 3) ** (1 / 3), 5 * 10 ** 7, Vec2(0, 0)
            )
        ]

        for j in range(1, 5):
            for i in range(0, j * 50):
                angle = 2 * math.pi * (i / (j * 50))
                mass = randint(1000, 100000 * (i+1))
                radius = (mass / 3) ** (1 / 3)
                planets.append(Planet(
                    j * (5000 + randint(-1000, 1000)) * math.sin(angle),
                    j * (5000 + randint(-1000, 1000)) * math.cos(angle),
                    radius,
                    mass,
                    Vec2(-randint(30*2, 70*2) * j * math.sin(angle) + randint(30*2, 70*2) * j * math.cos(angle),
                         -randint(30*2, 70*2) * j * math.cos(angle) - randint(30*2, 70*2) * j * math.sin(angle))
                ))

        planets.sort(key=lambda planet: planet.mass)
        self.physics = PhysicsEngine(planets)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = True
        if symbol == arcade.key.D:
            self.right_pressed = True
        if symbol == arcade.key.W:
            self.up_pressed = True
        if symbol == arcade.key.S:
            self.down_pressed = True
        if symbol == arcade.key.EQUAL:
            self.curr_size *= 10
        if symbol == arcade.key.MINUS:
            self.curr_size //= 10

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.A:
            self.left_pressed = False
        if symbol == arcade.key.D:
            self.right_pressed = False
        if symbol == arcade.key.W:
            self.up_pressed = False
        if symbol == arcade.key.S:
            self.down_pressed = False

    def on_update(self, delta_time: float):
        self.physics.update(delta_time)

        move = Vec2(
            delta_time * config.CAMERA_SPEED * (self.right_pressed - self.left_pressed),
            delta_time * config.CAMERA_SPEED * (self.up_pressed - self.down_pressed)
        )

        self.camera.position_excepted += Vec2(
            move.x * self.camera.zoom,
            move.y * self.camera.zoom
        )

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == 1 and modifiers == 17:
            self.mouse_pos_begin = Vec2(x, y)

            x = self.camera.x + (x - config.WIDTH / 2) * self.camera.zoom
            y = self.camera.y + (y - config.HEIGHT / 2) * self.camera.zoom

            self.creating = True
            self.pos = Vec2(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == 1 and modifiers == 17:
            x = self.camera.x + (x - config.WIDTH / 2) * self.camera.zoom
            y = self.camera.y + (y - config.HEIGHT / 2) * self.camera.zoom

            self.physics.planets.append(Planet(
                self.pos.x, self.pos.y,
                (self.curr_size / 3) ** (1 / 3),
                self.curr_size,
                Vec2((self.pos.x - x) / 5, (self.pos.y - y) / 5)
            ))
            self.creating = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        self.camera.zoom_excepted -= scroll_y * config.ZOOM_SPEED
        self.camera.zoom_excepted = max(self.camera.zoom_excepted, config.MIN_ZOOM)
        self.camera.zoom_excepted = min(self.camera.zoom_excepted, config.MAX_ZOOM)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        self.mouse_pos = Vec2(x, y)
        if modifiers != 17:
            self.camera.position_excepted += Vec2(
                -dx * self.camera.zoom,
                -dy * self.camera.zoom
            )

    def on_draw(self):
        self.clear()

        self.camera.update()
        arcade.set_viewport(
            self.camera.x - (config.WIDTH / 2) * self.camera.zoom,
            self.camera.x + (config.WIDTH / 2) * self.camera.zoom,
            self.camera.y - (config.HEIGHT / 2) * self.camera.zoom,
            self.camera.y + (config.HEIGHT / 2) * self.camera.zoom
        )

        for planet in self.physics.planets:
            arcade.draw_circle_filled(
                planet.x,
                planet.y,
                planet.r,
                arcade.color.WHITE)

        self.gui_camera.use()

        if self.creating:
            x = self.camera.x + (self.mouse_pos.x - config.WIDTH / 2) * self.camera.zoom
            y = self.camera.y + (self.mouse_pos.y - config.HEIGHT / 2) * self.camera.zoom

            arcade.draw_line(self.mouse_pos_begin.x, self.mouse_pos_begin.y, self.mouse_pos.x, self.mouse_pos.y,
                             arcade.color.GRAY, 3)
            arcade.draw_circle_filled(self.mouse_pos_begin.x, self.mouse_pos_begin.y, 5, arcade.color.RED)
            speed = (((self.pos.x - x) / 5) ** 2 + ((self.pos.y - y) / 5) ** 2) ** 0.5
            arcade.draw_text(f"{speed:0.2f}",
                             (self.mouse_pos_begin.x + self.mouse_pos.x) / 2,
                             (self.mouse_pos_begin.y + self.mouse_pos.y) / 2,
                             arcade.csscolor.WHITE,
                             16
                             )

        for i in range(len(self.gui_fields)):
            arcade.draw_text(f"{self.gui_fields[i][0]} {self.gui_fields[i][1]():0.2f}",
                             10,
                             config.HEIGHT - (i + 1) * 20,
                             arcade.csscolor.WHITE,
                             16
                             )
