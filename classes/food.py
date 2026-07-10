import pygame
import random
from settings import LARGURA, ALTURA, TAMANHO_BLOCO, VERMELHO


class Food:
    def __init__(self):
        self.posicao = self.gerar_posicao()

    def gerar_posicao(self, snake_corpo=None):
        while True:
             x = random.randrange(TAMANHO_BLOCO, LARGURA - TAMANHO_BLOCO, TAMANHO_BLOCO)
             y = random.randrange(40, ALTURA - TAMANHO_BLOCO, TAMANHO_BLOCO) #para evitar de nascer comida atrás das letras de score

             nova_posicao = (x, y)

             if snake_corpo is None or nova_posicao not in snake_corpo:
                return nova_posicao

    def desenhar(self, tela):
        pygame.draw.rect(tela, VERMELHO, (self.posicao[0], self.posicao[1], TAMANHO_BLOCO, TAMANHO_BLOCO))