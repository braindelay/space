import pygame
import sys

from modules.celestial import Celestial
from modules.game import Player, Game
from pygame.locals import *
from modules.ship import Ship

from modules.settings import screen, width,height, black

pygame.init()
pygame.mixer.set_num_channels(3)


clock = pygame.time.Clock()



def intro():
    text_lines = [
        [80, "Astro Battles!!!!"],
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
    sun = Celestial("resources/images/sun.jpg", 100, 0, 1)

    player1 = Player(1, Celestial("resources/images/player1.png", mass=20, radius=75, eccentricity=0.95))
    player2 = Player(2, Celestial("resources/images/player2.png", mass=10, radius=340, eccentricity=0.95))
    planets = [
        sun,
        Celestial("resources/images/planet.png", mass=10, radius=50, eccentricity=0.95),
        player1.celestial,
        Celestial("resources/images/planet.png", mass=15, radius=123, eccentricity=1.05),
        Celestial("resources/images/planet.png", mass=10, radius=175, eccentricity=0.90),
        Celestial("resources/images/planet.png", mass=10, radius=250, eccentricity=0.85),
        Celestial("resources/images/planet.png", mass=20, radius=300, eccentricity=0.95),
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
