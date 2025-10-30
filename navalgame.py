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

# --- Clase para las Olas (Efecto visual del barco) ---
class Ola(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._layer = 2 
        self.radio_inicial = random.randint(5, 10)
        self.radio = self.radio_inicial
        self.velocidad_expansion = random.uniform(0.2, 0.5)
        self.color = (200, 200, 255) 
        self.vida_util = random.randint(40, 80)
        self.contador_vida = 0
        self.image = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color + (100,), (self.radio, self.radio), self.radio, 1)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.contador_vida += 1
        if self.contador_vida > self.vida_util:
            self.kill()
            return
        self.radio += self.velocidad_expansion
        alpha = max(0, 255 * (1 - (self.contador_vida / self.vida_util)))
        centro_actual = self.rect.center
        self.image = pygame.Surface((int(self.radio * 2), int(self.radio * 2)), pygame.SRCALPHA)
        color_actual = self.color + (int(alpha),)
        pygame.draw.circle(self.image, color_actual, (int(self.radio), int(self.radio)), int(self.radio), 1)
        self.rect = self.image.get_rect(center=centro_actual)

# --- Clase para el Jugador (Barco) ---
class Jugador(pygame.sprite.Sprite):
    def __init__(self, ruta_assets):
        super().__init__()
        
        self.imagenes_barco = []
        try:
            barco1 = pygame.image.load(os.path.join(ruta_assets, "barco.png")).convert_alpha()
            barco2 = pygame.image.load(os.path.join(ruta_assets, "barco2.png")).convert_alpha()
            escala_barco1 = (70, 52) 
            escala_barco2 = (70, 52) 
            self.imagenes_barco.append(pygame.transform.scale(barco1, escala_barco1))
            self.imagenes_barco.append(pygame.transform.scale(barco2, escala_barco2))
        except pygame.error as e:
            print(f"Error al cargar imágenes del barco: {e}")
            fallback_surface = pygame.Surface((70, 52))
            fallback_surface.fill(COLOR_BLANCO)
            self.imagenes_barco = [fallback_surface, fallback_surface]

        self.image = self.imagenes_barco[0]
        self.rect = self.image.get_rect()
        
        self.sombra = self.crear_sombra(self.image)
        self.sombra_offset = (4, 4) 
        
        self.rect.centerx = ANCHO_PANTALLA // 2
        self.rect.bottom = ALTO_PANTALLA - 10
        self.velocidad_x = 0
        self.cadencia_disparo = 500 
        self.ultimo_disparo = pygame.time.get_ticks()
        self.cadencia_olas = 100
        self.ultima_ola = pygame.time.get_ticks()

    def crear_sombra(self, imagen):
        """Crea una superficie de sombra semitransparente para una imagen."""
        sombra = imagen.copy()
        sombra.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        sombra.set_alpha(100) 
        return sombra

    def cambiar_aspecto(self, nivel):
        """Cambia la imagen del barco Y su sombra según el nivel."""
        if nivel >= 2:
            self.image = self.imagenes_barco[1]
        else:
            self.image = self.imagenes_barco[0]
        pos_actual = self.rect.center
        self.rect = self.image.get_rect(center=pos_actual)
        self.sombra = self.crear_sombra(self.image)

    def generar_olas(self):
        ahora = pygame.time.get_ticks()
        if self.velocidad_x != 0 and ahora - self.ultima_ola > self.cadencia_olas:
            self.ultima_ola = ahora
            pos_ola_izquierda = (self.rect.left, self.rect.centery + 10)
            pos_ola_derecha = (self.rect.right, self.rect.centery + 10)
            return [Ola(*pos_ola_izquierda), Ola(*pos_ola_derecha)]
        return []

    def update(self):
        self.velocidad_x = 0
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.velocidad_x = -VELOCIDAD_JUGADOR
        if teclas[pygame.K_RIGHT]:
            self.velocidad_x = VELOCIDAD_JUGADOR
            
        self.rect.x += self.velocidad_x
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA

    def disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.cadencia_disparo:
            self.ultimo_disparo = ahora
            return DisparoJugador(self.rect.centerx, self.rect.top)
        return None

# --- Clase para el Disparo del Jugador ---
class DisparoJugador(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self._layer = 4
        self.image = pygame.Surface((5, 10))
        self.image.fill((0, 255, 0)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad_y = -8

    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.bottom < 0:
            self.kill()

# --- Clase para las Bombas ---
class Bomba(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo_bomba=1):
        super().__init__()
        self._layer = 4
        self.tipo_bomba = tipo_bomba
        if self.tipo_bomba == 1:
            self.image = pygame.Surface((8, 16))
            self.image.fill((255, 255, 0)) 
            self.velocidad_y = 5
        elif self.tipo_bomba == 2:
            self.image = pygame.Surface((10, 20))
            self.image.fill((255, 100, 0))
            self.velocidad_y = 7
        else: 
            self.image = pygame.Surface((6, 12))
            self.image.fill((0, 255, 255))
            self.velocidad_y = 9
        self.rect = self.image.get_rect(center=(x, y))
        
        self.sombra = self.crear_sombra(self.image)
        self.sombra_offset = (3, 3)

    def crear_sombra(self, imagen):
        sombra = imagen.copy()
        sombra.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        sombra.set_alpha(100)
        return sombra

    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO_PANTALLA:
            self.kill()

# --- Clase para el Enemigo (Avión) ---
class Enemigo(pygame.sprite.Sprite):
    def __init__(self, ruta_assets):
        super().__init__()
        self._layer = 4
        
        self.imagenes_avion = []
        try:
            avion1 = pygame.image.load(os.path.join(ruta_assets, "avion.png")).convert_alpha()
            avion2 = pygame.image.load(os.path.join(ruta_assets, "avion2.png")).convert_alpha()
            avion3 = pygame.image.load(os.path.join(ruta_assets, "avion3.png")).convert_alpha()
            
            escala1 = (45, 31)
            escala2 = (55, 36)
            escala3 = (65, 45)
            
            self.imagenes_avion.append(pygame.transform.scale(avion1, escala1))
            self.imagenes_avion.append(pygame.transform.scale(avion2, escala2))
            self.imagenes_avion.append(pygame.transform.scale(avion3, escala3))
        except pygame.error as e:
            print(f"Error al cargar imágenes de avión: {e}")
            fallback_surface = pygame.Surface((45, 31))
            fallback_surface.fill((200, 0, 0))
            self.imagenes_avion = [fallback_surface, fallback_surface, fallback_surface]

        self.tipo_enemigo = random.randint(1, 3)
        self.image = self.imagenes_avion[self.tipo_enemigo - 1]
        self.rect = self.image.get_rect()
        
        self.sombra = self.crear_sombra(self.image)
        self.sombra_offset = (4, 4)
        
        self.rect.x = random.randint(0, ANCHO_PANTALLA - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.velocidad_y = random.randint(2, 4)
        
        if self.tipo_enemigo == 1: 
            self.amplitud_onda = random.randint(50, 150)
            self.frecuencia_onda = random.uniform(0.01, 0.03)
            self.centro_x = self.rect.centerx
            self.angulo = 0
            self.velocidad_y = random.randint(2, 4)
            self.cadencia_disparo = 60 
            self.tipo_bomba = 1
        elif self.tipo_enemigo == 2: 
            self.velocidad_y = random.randint(4, 6)
            self.cadencia_disparo = 45 
            self.tipo_bomba = 2
        elif self.tipo_enemigo == 3: 
            self.velocidad_y = random.randint(2, 3)
            self.velocidad_x_zigzag = random.choice([-2, 2])
            self.cambio_zigzag_timer = random.randint(30, 90) 
            self.contador_zigzag = 0
            self.cadencia_disparo = 90 
            self.tipo_bomba = 3

        self.ultimo_disparo = pygame.time.get_ticks()

    def crear_sombra(self, imagen):
        sombra = imagen.copy()
        sombra.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        sombra.set_alpha(100)
        return sombra

    def update(self):
        self.rect.y += self.velocidad_y
        
        if self.tipo_enemigo == 1:
            self.angulo += self.frecuencia_onda
            offset_x = self.amplitud_onda * pygame.math.Vector2(1, 0).rotate(self.angulo * 180 / 3.14159).y
            self.rect.centerx = self.centro_x + offset_x
        elif self.tipo_enemigo == 3: 
            self.contador_zigzag += 1
            if self.contador_zigzag >= self.cambio_zigzag_timer:
                self.velocidad_x_zigzag *= -1 
                self.contador_zigzag = 0
                self.cambio_zigzag_timer = random.randint(30, 90)
            self.rect.x += self.velocidad_x_zigzag
            if self.rect.left < 0 or self.rect.right > ANCHO_PANTALLA:
                self.velocidad_x_zigzag *= -1
                self.rect.x += self.velocidad_x_zigzag 

        if self.rect.top > ALTO_PANTALLA:
            self.kill()

    def disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.cadencia_disparo * (1000 / FPS):
            self.ultimo_disparo = ahora
            return Bomba(self.rect.centerx, self.rect.bottom, self.tipo_bomba)
        return None

# --- Clase Principal del Juego ---
class Juego:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        
        ### MARCA: Añadida al título de la ventana ###
        pygame.display.set_caption("Defensor Naval - por Papiweb desarrollos informaticos")
        
        self.reloj = pygame.time.Clock()
        
        self.directorio_juego = os.path.dirname(os.path.abspath(__file__))
        self.directorio_assets = os.path.join(self.directorio_juego, "assets")

        # Cargar sonidos
        try:
            self.sonido_explosion = pygame.mixer.Sound(os.path.join(self.directorio_assets, "fall.mp3"))
            self.sonido_disparo = pygame.mixer.Sound(os.path.join(self.directorio_assets, "gun.mp3"))
            self.musica_presentacion = os.path.join(self.directorio_assets, "epic.mp3")
            self.musica_theme = os.path.join(self.directorio_assets, "theme.mp3")
            self.musica_dance = os.path.join(self.directorio_assets, "dance.mp3")
            self.musica_score = os.path.join(self.directorio_assets, "score.mp3")
            self.musica_actual = self.musica_theme
        except pygame.error as e:
            print(f"Error al cargar audio: {e}")
            self.sonido_explosion = None
            self.sonido_disparo = None
            self.musica_presentacion = None
            self.musica_theme = None

        # Cargar assets de la presentación
        try:
            self.fondo_presentacion = pygame.image.load(os.path.join(self.directorio_assets, "presentacion.png")).convert()
            self.fondo_presentacion = pygame.transform.scale(self.fondo_presentacion, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.imagenes_adelanto = [
                pygame.transform.scale(pygame.image.load(os.path.join(self.directorio_assets, "barco.png")).convert_alpha(), (160, 120)),
                pygame.transform.scale(pygame.image.load(os.path.join(self.directorio_assets, "avion.png")).convert_alpha(), (100, 70)),
                pygame.transform.scale(pygame.image.load(os.path.join(self.directorio_assets, "barco2.png")).convert_alpha(), (160, 120)),
                pygame.transform.scale(pygame.image.load(os.path.join(self.directorio_assets, "avion2.png")).convert_alpha(), (120, 80)),
                pygame.transform.scale(pygame.image.load(os.path.join(self.directorio_assets, "avion3.png")).convert_alpha(), (140, 100)),
            ]
        except pygame.error as e:
            print(f"Error al cargar imágenes de la presentación: {e}")
            self.fondo_presentacion = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
            self.fondo_presentacion.fill(COLOR_MAR)
            self.imagenes_adelanto = []

        # Variables para la transición de música
        self.transicionando_musica = False
        self.volumen_objetivo = 0.5
        self.tiempo_transicion = 1000 
        self.volumen_inicial_transicion = 0.0
        self.volumen_final_transicion = 0.0
        self.tiempo_inicio_transicion = 0
        self.ALTERNAR_MUSICA = pygame.USEREVENT + 2
        pygame.time.set_timer(self.ALTERNAR_MUSICA, 30000) 

        # Cargar fondos de niveles
        self.fondos = []
        try:
            fondo1 = pygame.image.load(os.path.join(self.directorio_assets, "fondo.png")).convert()
            fondo2 = pygame.image.load(os.path.join(self.directorio_assets, "fondo2.png")).convert()
            fondo3 = pygame.image.load(os.path.join(self.directorio_assets, "fondo3.png")).convert()
            fondo_score = pygame.image.load(os.path.join(self.directorio_assets, "score.png")).convert()
            self.fondos.append(pygame.transform.scale(fondo1, (ANCHO_PANTALLA, ALTO_PANTALLA)))
            self.fondos.append(pygame.transform.scale(fondo2, (ANCHO_PANTALLA, ALTO_PANTALLA)))
            self.fondos.append(pygame.transform.scale(fondo3, (ANCHO_PANTALLA, ALTO_PANTALLA)))
            self.fondos_score = pygame.transform.scale(fondo_score, (ANCHO_PANTALLA, ALTO_PANTALLA))
        except pygame.error as e:
            print(f"Error al cargar imágenes de fondo: {e}")
            fallback_fondo = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
            fallback_fondo.fill(COLOR_MAR)
            self.fondos = [fallback_fondo, fallback_fondo, fallback_fondo]
            self.fondos_score = fallback_fondo

        # Sistema de puntuación y niveles
        self.puntuacion = 0
        self.vidas = 3
        self.nivel = 1
        self.font = pygame.font.Font(None, 36)
        
        ### MARCA: Fuente para el texto de la marca ###
        self.font_marca = pygame.font.Font(None, 24)

        # Sistema de Highscore
        self.highscores = []
        self.nombre_jugador = ""
        self.cargar_highscores()

        # Grupos de Sprites
        self.todos_los_sprites = pygame.sprite.LayeredUpdates()
        self.particulas = pygame.sprite.Group()
        self.olas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.bombas_enemigas = pygame.sprite.Group()
        self.disparos_jugador = pygame.sprite.Group()
        
        self.jugador = Jugador(self.directorio_assets)
        self.jugador._layer = 3
        self.todos_los_sprites.add(self.jugador)
        
        self.ADDENEMY = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ADDENEMY, 1000) 
        self.jugando = True

    def pantalla_presentacion(self):
        if self.musica_presentacion:
            pygame.mixer.music.load(self.musica_presentacion)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.7)

        indice_imagen = 0
        ultimo_cambio = pygame.time.get_ticks()
        duracion_imagen = 2000 
        presentacion_activa = True

        while presentacion_activa:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN or evento.type == pygame.MOUSEBUTTONDOWN:
                    presentacion_activa = False

            self.pantalla.blit(self.fondo_presentacion, (0, 0))
            ahora = pygame.time.get_ticks()
            if ahora - ultimo_cambio > duracion_imagen and self.imagenes_adelanto:
                indice_imagen = (indice_imagen + 1) % len(self.imagenes_adelanto)
                ultimo_cambio = ahora

            if self.imagenes_adelanto:
                imagen_actual = self.imagenes_adelanto[indice_imagen]
                rect_imagen = imagen_actual.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
                self.pantalla.blit(imagen_actual, rect_imagen)

            self.dibujar_texto("Defensor Naval", 60, ANCHO_PANTALLA // 2 - 200, 50, self.font)
            self.dibujar_texto("Presiona cualquier tecla para comenzar", 30, ANCHO_PANTALLA // 2 - 250, ALTO_PANTALLA - 100, self.font)
            
            ### MARCA: Dibujar texto de la marca en la pantalla de presentación ###
            texto_marca = "Un juego de: Papiweb desarrollos informaticos"
            # Centrar el texto de la marca
            ancho_texto_marca = self.font_marca.size(texto_marca)[0]
            pos_x_marca = (ANCHO_PANTALLA - ancho_texto_marca) // 2
            self.dibujar_texto(texto_marca, 24, pos_x_marca, ALTO_PANTALLA - 50, self.font_marca)


            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.mixer.music.stop()
        if self.musica_theme:
            pygame.mixer.music.load(self.musica_theme)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)

    def ejecutar(self):
        self.pantalla_presentacion()
        while self.jugando:
            self.reloj.tick(FPS)
            self.eventos() 
            self.actualizar() 
            self.dibujar()    
        
        self.pantalla_game_over()

    def cambiar_musica(self):
        pygame.mixer.music.stop()
        try:
            if self.musica_actual == self.musica_theme:
                pygame.mixer.music.load(self.musica_dance)
                self.musica_actual = self.musica_dance
            else:
                pygame.mixer.music.load(self.musica_theme)
                self.musica_actual = self.musica_theme
            
            pygame.mixer.music.play(-1)
            self.volumen_inicial_transicion = 0.0
            self.volumen_final_transicion = self.volumen_objetivo
            self.tiempo_inicio_transicion = pygame.time.get_ticks()
            self.transicionando_musica = True
            pygame.mixer.music.set_volume(0.0)
        except Exception as e:
            print(f"Error al cambiar música: {e}")

    def manejar_transicion_musica(self):
        if not self.transicionando_musica:
            return
        
        ahora = pygame.time.get_ticks()
        tiempo_pasado = ahora - self.tiempo_inicio_transicion
        
        if tiempo_pasado >= self.tiempo_transicion:
            pygame.mixer.music.set_volume(self.volumen_final_transicion)
            self.transicionando_musica = False
        else:
            progreso = tiempo_pasado / self.tiempo_transicion
            volumen_actual = self.volumen_inicial_transicion + (self.volumen_final_transicion - self.volumen_inicial_transicion) * progreso
            pygame.mixer.music.set_volume(volumen_actual)

    def actualizar(self):
        self.todos_los_sprites.update()
        self.manejar_transicion_musica()

        nuevas_olas = self.jugador.generar_olas()
        if nuevas_olas:
            self.olas.add(nuevas_olas)
            self.todos_los_sprites.add(nuevas_olas)
        
        for enemigo in self.enemigos:
            bomba = enemigo.disparar()
            if bomba:
                self.bombas_enemigas.add(bomba)
                self.todos_los_sprites.add(bomba)

        # Colisiones: Disparos del Jugador vs Enemigos
        colisiones_jugador_enemigo = pygame.sprite.groupcollide(self.disparos_jugador, self.enemigos, True, True)
        for disparo, enemigos_alcanzados in colisiones_jugador_enemigo.items():
            for enemigo in enemigos_alcanzados:
                if self.sonido_explosion:
                    self.sonido_explosion.play()
                self.puntuacion += 100 
                for _ in range(20): 
                    particula = Particula(enemigo.rect.centerx, enemigo.rect.centery)
                    self.particulas.add(particula)
                    self.todos_los_sprites.add(particula)

        # Colisiones: Bombas Enemigas vs Jugador
        colisiones_bomba_jugador = pygame.sprite.spritecollide(self.jugador, self.bombas_enemigas, True)
        if colisiones_bomba_jugador:
            if self.sonido_explosion:
                self.sonido_explosion.play()
            self.vidas -= 1
            for _ in range(30):
                particula = Particula(self.jugador.rect.centerx, self.jugador.rect.centery)
                self.particulas.add(particula)
                self.todos_los_sprites.add(particula)
            
            self.jugador.rect.centerx = ANCHO_PANTALLA // 2
            self.jugador.rect.bottom = ALTO_PANTALLA - 10
            if self.vidas <= 0:
                self.jugando = False 

        # Control de Niveles
        puntos_para_nivel = self.nivel * 1500 
        if self.puntuacion >= puntos_para_nivel:
            self.nivel += 1
            if self.nivel > 3: 
                self.nivel = 3 
            
            nueva_cadencia = max(200, 1000 - (self.nivel * 200)) 
            pygame.time.set_timer(self.ADDENEMY, nueva_cadencia)
            self.jugador.cambiar_aspecto(self.nivel)

    def dibujar(self):
        # Dibujar el fondo
        fondo_idx = min(self.nivel - 1, len(self.fondos) - 1)
        self.pantalla.blit(self.fondos[fondo_idx], (0, 0))
        
        # Sombra del jugador
        sombra_pos_x = self.jugador.rect.x + self.jugador.sombra_offset[0]
        sombra_pos_y = self.jugador.rect.y + self.jugador.sombra_offset[1]
        self.pantalla.blit(self.jugador.sombra, (sombra_pos_x, sombra_pos_y))
        
        # Sombras de enemigos
        for enemigo in self.enemigos:
             sombra_pos_x = enemigo.rect.x + enemigo.sombra_offset[0]
             sombra_pos_y = enemigo.rect.y + enemigo.sombra_offset[1]
             self.pantalla.blit(enemigo.sombra, (sombra_pos_x, sombra_pos_y))

        # Sombras de bombas
        for bomba in self.bombas_enemigas:
             sombra_pos_x = bomba.rect.x + bomba.sombra_offset[0]
             sombra_pos_y = bomba.rect.y + bomba.sombra_offset[1]
             self.pantalla.blit(bomba.sombra, (sombra_pos_x, sombra_pos_y))
        
        # Dibujar todos los sprites
        self.todos_los_sprites.draw(self.pantalla)
        
        # Dibujar la UI
        self.dibujar_texto(f"Puntuación: {self.puntuacion}", 36, 10, 10, self.font)
        self.dibujar_texto(f"Vidas: {self.vidas}", 36, ANCHO_PANTALLA - 150, 10, self.font)
        self.dibujar_texto(f"Nivel: {self.nivel}", 36, ANCHO_PANTALLA // 2 - 50, 10, self.font)

        pygame.display.flip()

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.jugando = False
            
            if evento.type == self.ADDENEMY:
                nuevo_enemigo = Enemigo(self.directorio_assets) 
                self.enemigos.add(nuevo_enemigo)
                self.todos_los_sprites.add(nuevo_enemigo)

            if evento.type == self.ALTERNAR_MUSICA:
                self.cambiar_musica()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    disparo = self.jugador.disparar()
                    if disparo:
                        if self.sonido_disparo:
                            self.sonido_disparo.play()
                        self.disparos_jugador.add(disparo)
                        self.todos_los_sprites.add(disparo)

    def dibujar_texto(self, texto, tamano, x, y, fuente):
        superficie_texto = fuente.render(texto, True, COLOR_BLANCO)
        rect_texto = superficie_texto.get_rect()
        rect_texto.topleft = (x, y)
        self.pantalla.blit(superficie_texto, rect_texto)

    def cargar_highscores(self):
        try:
            with open(os.path.join(self.directorio_juego, "highscores.json"), "r") as f:
                self.highscores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.highscores = []

    def guardar_highscores(self):
        if self.puntuacion > 0:
            self.highscores.append({"nombre": self.nombre_jugador if self.nombre_jugador else "AAA", "puntuacion": self.puntuacion})
        
        self.highscores = sorted(self.highscores, key=lambda x: x["puntuacion"], reverse=True)[:10] 
        with open(os.path.join(self.directorio_juego, "highscores.json"), "w") as f:
            json.dump(self.highscores, f, indent=4)

    def pantalla_game_over(self):
        if hasattr(self, 'musica_score') and self.musica_score:
            pygame.mixer.music.load(self.musica_score)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.6)

        font_grande = pygame.font.Font(None, 60)
        font_mediana = pygame.font.Font(None, 36)
        font_pequena = pygame.font.Font(None, 30)

        input_activo = True
        if self.puntuacion == 0 or (len(self.highscores) >= 10 and self.puntuacion < self.highscores[-1]["puntuacion"]):
             input_activo = False
             self.guardar_highscores() 

        game_over_loop = True
        while game_over_loop:
            self.pantalla.blit(self.fondos_score, (0, 0))
            self.dibujar_texto("GAME OVER", 60, ANCHO_PANTALLA // 2 - 140, 50, font_grande)
            self.dibujar_texto(f"Tu Puntuación: {self.puntuacion}", 36, ANCHO_PANTALLA // 2 - 120, 120, font_mediana)
            
            self.dibujar_texto("Highscores:", 36, ANCHO_PANTALLA // 2 - 120, 180, font_mediana)
            y_offset = 220
            for i, score in enumerate(self.highscores):
                self.dibujar_texto(f"{i+1}. {score['nombre']}: {score['puntuacion']}", 30, ANCHO_PANTALLA // 2 - 120, y_offset + i * 30, font_pequena)

            if input_activo:
                self.dibujar_texto("¡Nuevo Highscore! Ingresa tu nombre:", 30, ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA - 100, font_pequena)
                caja_rect = pygame.Rect(ANCHO_PANTALLA // 2 - 100, ALTO_PANTALLA - 60, 200, 32)
                pygame.draw.rect(self.pantalla, COLOR_BLANCO, caja_rect, 2)
                self.dibujar_texto(self.nombre_jugador, 30, caja_rect.x + 5, caja_rect.y + 5, font_pequena)
            else:
                self.dibujar_texto("Presiona R para reiniciar o Q para salir", 30, ANCHO_PANTALLA // 2 - 200, ALTO_PANTALLA - 50, font_pequena)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if input_activo:
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_RETURN:
                            input_activo = False
                            self.guardar_highscores()
                        elif evento.key == pygame.K_BACKSPACE:
                            self.nombre_jugador = self.nombre_jugador[:-1]
                        elif len(self.nombre_jugador) < 10: 
                            self.nombre_jugador += evento.unicode
                else:
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_r:
                            game_over_loop = False 
                        if evento.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
            
            pygame.display.flip()
            self.reloj.tick(FPS)
        
        juego = Juego()
        juego.ejecutar()

# --- Iniciar el juego ---
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()