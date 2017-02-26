#
# The main game script - render the intro, and start the main game loop
#
#
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



#
# Draw the intro, and wait for a key press to start the game
#
def intro():
    # the text to render
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

    # now we scan through the text, and render it centered on the screen

    # get the total height, we move up half this value from the centre
    # so that the overall text will be centered
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

    # now, wait for a key to be pressed
    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN:
            break


#
# The main game loop
# - build the celestial elements (this includes the two players), the ship and the game
# - until the game is over, offer each player a chance to kill the other one ;)
#
def playGame():

    # build the solar system
    sun = Celestial("resources/images/sun.jpg", 100, 0, 1)

    player1 = Player(1, Celestial("resources/images/player1.png", mass=20, radius=75, eccentricity=0.95))
    player2 = Player(2, Celestial("resources/images/player2.png", mass=10, radius=340, eccentricity=0.95))

    # this collection is everything that can attract the ship
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

    # the game is over when all but one player is dead
    while not game.is_over():

        # this is listening for someone to close the window
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            sys.exit(0)

        # clear the screen
        screen.fill(black)

        # let the player know whose turn it is, and how
        # much fuel is left on the spaceship
        game.render_state()

        # move the planets in their orbits
        for p in planets:
            p.move()
            p.blit(screen)

        # move the ship by
        # - dragging it towards the sun and each planet
        # - if the player is pressing the direction keys, then apply that thrust
        if ship.is_launched:
            ship.apply_acceleration(planets)
            ship.move()

            # if the ship has hit something, or has run out of fuel, then
            # then it's the next player's turn
            # : if the ship hit a player and killed them then game.is_over()
            #   will say so
            game.check_collisions()
            if ship.is_ship_dead():
                game.next_player()

        else:
            # the ship isn't launched, so check if we've been asked
            # to do so
            game.check_launch_trigger()

        # redraw the frame, but we don't want a framerate > 40
        pygame.display.flip()
        clock.tick(40)

    # if we're here, then the game is over
    game.render_game_over()


#
# Ok,so now we do something ;)
#
# Draw the intro, and then keep playing games until someone closes
# the window
#
intro()
while 1:
    playGame()
