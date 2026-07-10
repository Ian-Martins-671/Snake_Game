import pygame

som_fundo = None
som_comer = None
som_game_over = None


def carregar_sons():
    global som_fundo, som_comer, som_game_over

    if pygame.mixer.get_init() is None:
        return

    if som_fundo is None:
        som_fundo = pygame.mixer.Sound("assets/somfundosnake.mp3")
        som_fundo.set_volume(0.1)

    if som_comer is None:
        som_comer = pygame.mixer.Sound("assets/food_sound.wav")
        som_comer.set_volume(0.1)

    if som_game_over is None:
        som_game_over = pygame.mixer.Sound("assets/deathSound.mp3")
        som_game_over.set_volume(0.2)


def tocar_som(canal, som, loops=0):
    if som is None:
        return

    try:
        canal.play(som, loops=loops)
    except pygame.error:
        pass

