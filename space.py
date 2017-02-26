import sys, pygame
from pygame.locals import *
from math import cos, sin, sqrt, pow, log, atan2, pi
from random import randint
import numpy as np

import time

pygame.init()
pygame.mixer.set_num_channels(3)

size = width, height = 700, 700
black = 0, 0, 0

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


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

    def pos(self):
        return np.array((float(self.rect.x), float(self.rect.y)))

    # attract the ship towards this celestial
    # this will directly edit the ship's acceleration vector
    def attract(self, ship):
        pos = self.pos()

        # basic newton
        direction = pos - ship.pos

        distance = np.sqrt(np.sum((direction) ** 2))
        if abs(direction) is not 0:
            unit_vector = direction / abs(direction)

            G = 5
            acceleration = G * self.mass * unit_vector / pow(distance, 2)

            ship.acceleration += acceleration


# The ship type		
class Ship(SpaceElement):
    def __init__(self):
        SpaceElement.__init__(self, "ship.png")

        self.thrusters = pygame.mixer.Sound("thrusters.wav")
        self.breakdown = pygame.mixer.Sound("breakdown.wav")

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
            return "Remaining fuel: %s%s" % (self.fuel, debug)
        else:
            return "Press direction to launch"


# simple player model
class Player:
    def __init__(self, id, celestial):
        self.id = id
        self.celestial = celestial
        self.life = 100


# the game model
class Game:
    def __init__(self, players, ship, celestials, screen):
        self.players = players
        self.current_player_id = None
        self.ship = ship
        self.screen = screen
        self.celestials = celestials
        self.next_player()

        self.explosion_channel = pygame.mixer.Channel(2)
        self.explosion = pygame.mixer.Sound("explosion.wav")

    # advance to the next player- this resets the ship, etc
    def next_player(self):
        self.ship.reset()
        self.is_launch_allowed = False

        if self.current_player_id is None:
            self.current_player_id = 0
        else:
            self.current_player_id += 1
            self.current_player_id %= len(self.players)

        self.prepare_for_launch = pygame.time.get_ticks()

    # get the current player object
    def current_player(self):
        return self.players[self.current_player_id]

    # draw the current state
    def render_state(self):
        # the current state of the current player
        player_message = "Player: %s ; life: %s" % (
            self.current_player_id + 1,
            self.current_player().life
        )

        # there is a gap when we're not allowed to launch
        # in this period we show a different message
        deltaTime = (pygame.time.get_ticks() - self.prepare_for_launch)
        if deltaTime < 3000 and not self.ship.is_launched:
            activity_message = "ready to launch in: %s" % (3 - int(deltaTime / 1000.0))
        else:
            self.is_launch_allowed = True
            activity_message = self.ship.get_render_message()

        # now, render the full message
        message = "%s - %s" % (player_message, activity_message)
        basicfont = pygame.font.SysFont(None, 20)
        text = basicfont.render(message, True, (255, 0, 0), (0, 0, 0))

        textrect = text.get_rect()
        screen.blit(text, textrect)

    # check - if launching allowed - if someone has launched the rocket
    def check_launch_trigger(self):
        if self.is_launch_allowed:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                self.ship.launch(self.current_player().celestial.pos())

    # check if we've hit anything
    def check_collisions(self):

        # we don't count collision during launch
        if not self.ship.is_launching:
            # if we hit a player, the player is damaged based on the remaining fuel
            for p in self.players:
                if self.ship.rect.colliderect(p.celestial.rect):
                    p.life -= self.ship.fuel
                    break

            # if we hit anything the ship can be destroyed
            for c in self.celestials:
                if self.ship.rect.colliderect(c.rect):
                    self.explosion_channel.play(self.explosion)
                    self.ship.fuel = 0
                    break

    # the game is over when one player has no more life
    def is_over(self):
        for p in self.players:
            if p.life <= 0:
                self.players.remove(p)

        return len(self.players) == 1

    def winner(self):
        return self.players[0]

    def render_game_over(self):
        screen.fill(black)

        basicfont = pygame.font.SysFont(None, 50)
        text = basicfont.render("Player %s wins!" % (self.winner().id), True, (255, 0, 0), (0, 0, 0))
        textrect = text.get_rect()
        textrect.center = (width / 2, height / 2)
        screen.blit(text, textrect)

        pygame.display.flip()
        time.sleep(3)


def intro():
    text_lines = [
        [80, "Newton Wars"],
        [30, "The second and seventh planets are in the midst"],
        [30, "of a terrible religious war"],
        [20, "(tabs or spaces)"],
        [40, "When it's your turn, use the direction buttons"],
        [40, "to guide your rocket to its target"],
        [30, "The less fuel you use, the more damage you do"],
        [40, "Press any key to start"],
    ]

    # get the heights
    total_height = sum([t[0] for t in text_lines])
    current_height = height / 2 - total_height / 2

    # render the texts
    for i in xrange(len(text_lines)):
        t = text_lines[i]
        basicfont = pygame.font.SysFont(None, t[0])
        current_height += t[0]
        text = basicfont.render(t[1], True, (255, 0, 0), (0, 0, 0))
        textrect = text.get_rect()
        textrect.center = (width / 2, current_height)
        screen.blit(text, textrect)

    pygame.display.flip()

    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN:
            break


def playGame():
    sun = Celestial("sun.jpg", 100, 0, 1)

    player1 = Player(1, Celestial("player1.png", mass=20, radius=75, eccentricity=0.95))
    player2 = Player(2, Celestial("player2.png", mass=10, radius=340, eccentricity=0.95))
    planets = [
        sun,
        Celestial("planet.png", mass=10, radius=50, eccentricity=0.95),
        player1.celestial,
        Celestial("planet.png", mass=15, radius=123, eccentricity=1.05),
        Celestial("planet.png", mass=10, radius=175, eccentricity=0.90),
        Celestial("planet.png", mass=10, radius=250, eccentricity=0.85),
        Celestial("planet.png", mass=20, radius=300, eccentricity=0.95),
        player2.celestial
    ]

    ship = Ship()

    game = Game([player1, player2], ship, planets, screen)

    while not game.is_over():
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            sys.exit(0)

        screen.fill(black)

        game.render_state()

        # move the planets
        for p in planets:
            p.move()
            p.blit(screen)

        # move the ship
        if ship.is_launched:
            ship.apply_acceleration(planets)
            ship.move()

            game.check_collisions()

            if ship.is_ship_dead():
                game.next_player()

        else:
            game.check_launch_trigger()

        # redraw the frame, but we don't want a framerate > 40
        pygame.display.flip()
        clock.tick(40)

    # if we're here, then the game is over
    game.render_game_over()


intro()
while 1:
    playGame()
