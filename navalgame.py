# Papiweb desarrollos informaticos
import pygame
import sys
import random
import json
import os 

# --- Constantes ---
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
COLOR_MAR = (0, 0, 50)
COLOR_BLANCO = (255, 255, 255)
FPS = 60
VELOCIDAD_JUGADOR = 5

# --- Clase para las Partículas de Explosión ---
class Particula(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self._layer = 5
		self.image = pygame.Surface((random.randint(2, 5), random.randint(2, 5)))
		self.image.fill(random.choice([(255, 0, 0), (255, 165, 0), (255, 255, 0)]))
		self.rect = self.image.get_rect(center=(x, y))
		self.velocidad_x = random.uniform(-2, 2)
		self.velocidad_y = random.uniform(-2, 2)
		self.vida_util = random.randint(15, 30) 
		self.contador_vida = 0

	def update(self):
		self.rect.x += self.velocidad_x
		self.rect.y += self.velocidad_y
		self.contador_vida += 1
		if self.contador_vida > self.vida_util:
			self.kill() 
        
		escala = 1 - (self.contador_vida / self.vida_util)
		ancho_original, alto_original = self.image.get_size()
		nuevo_ancho = max(1, int(ancho_original * escala))
		nuevo_alto = max(1, int(alto_original * escala))
		self.rect.width = nuevo_ancho
		self.rect.height = nuevo_alto

# ...existing code...
