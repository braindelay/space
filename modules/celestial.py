#
# Define the celestial objects - the base space element (we use this for the
# ship later on) and also for the planets
#
#
import pygame
from random import randint
from math import cos, sin
import numpy as np
from settings import width,height, screen

# A general space element, containsa sprite, etc
class SpaceElement:
    def __init__(self, image):
        self.sprite = pygame.image.load(image)
        self.rect = self.sprite.get_rect()


    # redraw the element
    def blit(self, screen):
        screen.blit(self.sprite, self.rect)





# A celestial object with mass and orbit - attracts the space ship to it
class Celestial(SpaceElement):
    def __init__(self, image, mass, radius, eccentricity):


        SpaceElement.__init__(self, image)
        self.mass = mass
        self.radius = radius
        self.eccentricity = eccentricity

        self.angle = randint(1, 360)
        self.angle_speed = 0.025 * (1 - (float(radius) / float(width / 2)))

    # move the object in its orbit
    def move(self):
        self.angle += self.angle_speed
        self.rect.x = width / 2 + self.radius * cos(self.angle)
        self.rect.y = height / 2 + self.eccentricity * self.radius * sin(self.angle)

    # get the position for this celestial object
    def pos(self):
        return np.array((float(self.rect.centerx), float(self.rect.centery)))

    # attract the ship towards this celestial
    # this will directly edit the ship's acceleration vector
    def attract(self, ship):
        pos = self.pos()

        # basic newton - but set up to work on the
        # map of pixels that we have
        direction = pos - ship.pos

        distance = np.sqrt(np.sum((direction) ** 2))
        if abs(direction).all() > 0.0:
            unit_vector = np.nan_to_num(direction / abs(direction))
            G = 5
            acceleration = G * self.mass * unit_vector / pow(distance, 2)
            ship.acceleration += acceleration

    # draw a circle around the planet
    def identify(self, colour, fill=1):
        pos = self.pos();
        pygame.draw.circle(screen, colour, (int(pos[0]),int(pos[1])), 15, fill)

    # if the planet has been hit, draw a flash circle around it
    def hit(self):
        self.identify( (255,0,0), 0)