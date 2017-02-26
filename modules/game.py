#
# This handles the players and the overall game model
# Mostly concerned with knowing what the game elements are
# up to. The actual game is driven from outside of this
#
#
import pygame
from settings import width,height,screen,black

import time
# simple player model
class Player:
    def __init__(self, id, celestial):
        self.id = id
        self.celestial = celestial
        self.total_life= 500.0
        self.life = self.total_life

        self.icon = pygame.transform.rotate(celestial.sprite, 0)
        self.icon_rect = self.icon.get_rect()


    def render_details(self, basicfont):

        # write some text about the player
        pid =self.id
        p_message = "Player: %s " % (pid)
        p_text = basicfont.render(p_message, True, (255, 0, 0), (0, 0, 0))
        p_textrect = p_text.get_rect()
        p_textrect.x = 30
        p_textrect.y = 20 * pid
        screen.blit(p_text, p_textrect)

        # draw the icon for the planet
        self.icon_rect.y = 20 * (pid) - 3
        screen.blit(self.icon,self.icon_rect)



        draw_gauge(100, pid * 20, self.total_life, self.life)


# Draw a rectangle gauge, 100 pixels wide, at the given point
def draw_gauge(x, y, total, current):
    ratio_remaining = (float(current) / float(total))

    width_remaining = 100 * ratio_remaining
    width_lost = 100 - width_remaining

    # change the colour depending on the remaining value
    colour = get_gauge_colour(ratio_remaining)


    # draw the remaining rectangle (filled) and if there's
    # any lost values, draw the rest of the gauge as an empty
    # rectangle
    pygame.draw.rect(screen, colour, (x, y, width_remaining, 18))
    if ratio_remaining < 1.0:
        pygame.draw.rect(screen, colour, (100 + width_remaining,y , width_lost, 18), 1)

def get_gauge_colour(ratio_remaining):
    if ratio_remaining > 0.5:
        return  (0, 255, 0)
    elif ratio_remaining > 0.25:
        return (255, 255, 0)
    else:
        return (255, 0, 0)

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

    # draw the current state, i.e.
    # - which player is on, and how much life is left
    # - can they launch the ship
    # - if they've launched, how much fuel have they left
    def render_state(self):
        # the current state of the current player
        player_message = "Player: %s " % (
            self.current_player_id + 1,
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

        # render the remaining fuel (if we're launched)
        if self.ship.is_launched:
            draw_gauge(100, 0, 100, self.ship.fuel)


        for p in self.players:
            p.render_details(basicfont)

            if self.current_player() == p:
                p.celestial.identify(get_gauge_colour(p.life / p.total_life))


    # check - if launching allowed - if someone has asked to launch the rocket
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
                    c.hit()
                    self.explosion_channel.play(self.explosion)
                    self.ship.fuel = 0
                    break

    # If the player _can_ shoot, but is delaying in order to get an
    # easyshot, we should punish them for taking their time by
    #healing the other players
    def heal_other_players(self):
        if self.is_launch_allowed and not self.ship.is_launched:
            # find all the other players, and heal them
            # if they're not dead
            for p in self.players:
                if p is not self.current_player() and p.life > 0 and p.life < p.total_life:
                    # we do this every 40th of a second
                    p.life += 5 / 40.0
    # the game is over when one player has no more life
    def is_over(self):
        for p in self.players:
            if p.life <= 0:
                self.players.remove(p)

        return len(self.players) == 1

    # get the winner - this is only valid if is_over returns True
    def winner(self):
        return self.players[0]

    # draw the game over message
    def render_game_over(self):
        screen.fill(black)

        basicfont = pygame.font.SysFont(None, 50)
        text = basicfont.render("Player %s wins!" % (self.winner().id), True, (255, 0, 0), (0, 0, 0))
        textrect = text.get_rect()
        textrect.center = (width / 2, height / 2)
        screen.blit(text, textrect)

        pygame.display.flip()
        time.sleep(3)

