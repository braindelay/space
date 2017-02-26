from celestial import SpaceElement
import pygame
from math import  atan2, pi
import numpy as np

from settings import screen

# The ship type
class Ship(SpaceElement):
    def __init__(self):
        SpaceElement.__init__(self, "resources/images/ship.png")

        self.thrusters = pygame.mixer.Sound("resources/sounds/thrusters.wav")
        self.breakdown = pygame.mixer.Sound("resources/sounds/breakdown.wav")

        self.explosion_channel = pygame.mixer.Channel(0)
        self.breakdown_channel = pygame.mixer.Channel(1)

        self.reset()

    def play_thrusters_sound(self):
        if not self.explosion_channel.get_busy():
            self.explosion_channel.play(self.thrusters)

    def stop_thrusers_sound(self):
        self.explosion_channel.stop()

    # hide the spaceship
    def reset(self):
        self.stop_thrusers_sound()
        self.is_launched = False
        self.is_launching = False

    # launch the space ship
    def launch(self, pos):

        # move us to the current player's planet and
        # initialise he vectors to nothing
        self.pos = pos
        self.speed = np.array((0.0, 0.0))
        self.acceleration = np.array((0.0, 0.0))

        # we start fully loaded
        self.fuel = 100

        # this will cause us to be rendered
        self.is_launched = True

        # this will cause planet gravity to not be counted
        # for a few seconds (during takeoff)
        self.is_launching = True
        self.launch_time = pygame.time.get_ticks()

    # move the ship
    def move(self):
        # this gets called all the time after the ship is launched
        # so we use this to record when we've finally taken-off
        deltaTime = (pygame.time.get_ticks() - self.launch_time)
        if deltaTime > 1000:
            self.is_launching = False

        # move the ship accordingto the acceleration
        self.speed += self.acceleration
        self.pos += self.speed

        # move the sprite to the position
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]

        # point the sprite in the directon we're moving
        angle = atan2(self.speed[0], self.speed[1]) * 180 / pi


        rotated = pygame.transform.rotate(self.sprite, angle)
        rotated_rect = rotated.get_rect()

        rotated_rect.x = self.pos[0]
        rotated_rect.y = self.pos[1]

        screen.blit(rotated, rotated_rect)

    # apply all accelerations to the ship
    # (both by control and by gravity)
    def apply_acceleration(self, planets):
        # reset the acceleration vector and then recalculate it
        # to include all the celestials and any ship control
        self.acceleration = np.array((0.0, 0.0))
        self.attractTo(planets)
        self.control()

    # attract the ship to all the listed planets
    # but only after we've fully taken off
    def attractTo(self, planets):
        if self.is_launched and not self.is_launching:
            for p in planets:
                p.attract(self)

    # apply any controls to the ship
    def control(self):
        if self.is_launched:
            acceleration = 0.125
            fuel_usage = -1
            keys = pygame.key.get_pressed()

            action = False
            if keys[pygame.K_LEFT]:
                self.acceleration[0] -= acceleration
                action = True
            if keys[pygame.K_RIGHT]:
                self.acceleration[0] += acceleration
                action = True
            if keys[pygame.K_UP]:
                self.acceleration[1] -= acceleration
                action = True
            if keys[pygame.K_DOWN]:
                self.acceleration[1] += acceleration
                action = True

            if action:
                self.play_thrusters_sound()
                self.fuel += fuel_usage
            else:
                self.stop_thrusers_sound()

            if self.fuel <= 0:
                self.play_dead()

    # does the ship needto be reset?
    def is_ship_dead(self):
        return self.fuel <= 0

    def play_dead(self):
        self.breakdown_channel.play(self.breakdown)

    # derive the current state message for the game
    def get_render_message(self):

        if self.is_launched:
            debug = ""
            return "Remaining fuel: %s%s: (%s.%s)" % (self.fuel, debug, self.rect.x,self.rect.y)
        else:
            return "Press direction to launch"

