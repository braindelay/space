import sys, pygame
from math import cos,sin,sqrt,pow
from random import randint
import numpy as np

pygame.init()

size = width, height = 700, 700
black = 0, 0, 0

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

class SpaceElement:
	def __init__(self, image):
		self.sprite = pygame.image.load(image)
		self.rect = self.sprite.get_rect()	

	def blit(self, screen):
		screen.blit(self.sprite, self.rect)

class Celestial(SpaceElement):
	def __init__(self, image, mass, radius, eccentricity):
		SpaceElement.__init__(self, image)
		self.mass = mass
		self.radius = radius
		self.eccentricity = eccentricity

		self.angle = randint(1,360)
		self.angle_speed = 0.01 *  (1.0 - float(radius)/float(width))


	def move(self):
		self.angle += self.angle_speed
		self.rect.x = width / 2 + self.radius * cos (self.angle)
		self.rect.y = height/ 2 + self.eccentricity * self.radius * sin (self.angle)

	def attract(self, ship):
		pos = np.array((float(self.rect.x),float(self.rect.y)))

		direction = pos - ship.pos
		distance = np.sqrt(np.sum((direction)**2))
		unit_vector = direction / abs(direction)

		G = 5
		acceleration =  G * self.mass * unit_vector / pow(distance, 2)

		ship.acceleration += acceleration


		
class Ship(SpaceElement):
	def __init__(self, start_x, start_y):
		SpaceElement.__init__(self, "ship.png")
		self.pos = np.array((float(start_x),float(start_y)))
		self.speed =np.array((0.0,0.0))
		self.acceleration= np.array((0.0,0.0))

		self.move()


	def move(self):
		self.speed += self.acceleration
		self.pos += self.speed

		self.rect.x = self.pos[0]
		self.rect.y = self.pos[1]

		print ("-----")
		print ("pos", self.pos)
		print ("speed", self.speed)
		print ("acc", self.acceleration)

	def apply_acceleration(self, planets):
		self.acceleration= np.array((0.0,0.0))
		self.attractTo(planets)
		self.control()

	def attractTo(self, planets):
		for p in planets:
			p.attract(self)
			
	def control(self):
		acceleration = 0.125
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]:
			self.acceleration[0]-=acceleration
		if keys[pygame.K_RIGHT]:
			self.acceleration[0]+=acceleration
		if keys[pygame.K_UP]:
			self.acceleration[1]-=acceleration
		if keys[pygame.K_DOWN]:
			self.acceleration[1]+=acceleration
def game():
	sun = Celestial("sun.jpg", 100, 0, 1)
	planets = [
		sun, 
		Celestial("planet.png", mass=10, radius=50, eccentricity=0.95),
		Celestial("planet.png", mass=15, radius=75, eccentricity=1.05),
		Celestial("planet.png", mass=20, radius=125, eccentricity=0.95),
		Celestial("planet.png", mass=10, radius=175, eccentricity=0.90),
		Celestial("planet.png", mass=10, radius=250, eccentricity=0.85),
		Celestial("planet.png", mass=10, radius=300, eccentricity=0.95),
		Celestial("planet.png", mass=20, radius=340, eccentricity=0.95),

	]

	ship = Ship(10, 10)


	while 1:
		event = pygame.event.poll()
		if event.type == pygame.QUIT:
			break	

		screen.fill(black)


		# move the planets
		for p in planets:
			p.move()
			p.blit(screen)

		# move the ship
		ship.blit(screen)
		
		ship.apply_acceleration(planets)
		ship.move()


		# redraw the frame, but we don't want a framerate > 40 
		pygame.display.flip()		
		clock.tick(40)


game()