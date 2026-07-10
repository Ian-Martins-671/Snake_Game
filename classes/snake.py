import pygame

from settings import TAMANHO_BLOCO, VERDE


class Snake:
    def __init__(self):
        self.corpo = [(300, 300)]
        self.direcao = (TAMANHO_BLOCO, 0)
        self.crescendo = False  # controla quando a cobra deve aumentar

    def mover(self):
        cabeca_x, cabeca_y = self.corpo[0]
        dx, dy = self.direcao

        nova_cabeca = (cabeca_x + dx, cabeca_y + dy)
        self.corpo.insert(0, nova_cabeca)

        # Movimento normal remove a cauda
        if not self.crescendo:
            self.corpo.pop()
        else:
            # Se comeu, mantém a cauda e cresce +1
            self.crescendo = False

    def crescer(self):
        # +1 bloco no próximo movimento
        self.crescendo = True

    def desenhar(self, tela):
        for bloco in self.corpo:pygame.draw.rect(tela, VERDE, (bloco[0], bloco[1], TAMANHO_BLOCO, TAMANHO_BLOCO))