import pygame
from settings import width,height,screen,black

import time
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
        self.explosion = pygame.mixer.Sound("resources/sounds/explosion.wav")

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

