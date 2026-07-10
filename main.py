import json
import math
import os
import random
import sys
from datetime import datetime

import pygame

from settings import *
from classes.food import Food
from classes.snake import Snake
import classes.sounds as sounds

pygame.mixer.pre_init(44100, -16, 2, 128)
pygame.init()
pygame.mixer.init()

sounds.carregar_sons()

canal_fundo = pygame.mixer.Channel(3)
canal_comer = pygame.mixer.Channel(1)
canal_death = pygame.mixer.Channel(2)

# Tela
tela = pygame.display.set_mode((LARGURA, ALTURA))

pygame.display.set_caption("S N A K E")
inicio = datetime.now()
print(f"Jogo iniciado às: {inicio.strftime('%H:%M:%S')}")


relogio = pygame.time.Clock()

ARQUIVO_RECORDES = "recordes.json"
ARQUIVO_PERFIS = "perfis.json"
MAX_RECORDES = 5

def criar_particulas():
    return [
        {
            "x": random.randint(0, LARGURA),
            "y": random.randint(0, ALTURA),
            "vx": random.uniform(-0.2, 0.2),
            "vy": random.uniform(-0.2, 0.2),
            "tamanho": random.randint(1, 3),
        }
        for _ in range(90)
    ]

def criar_estrelas():
    return [
        {
            "x": random.randint(0, LARGURA),
            "y": random.randint(0, ALTURA),
            "tamanho": random.randint(1, 3),
            "fase": random.uniform(0, 2 * math.pi),
            "velocidade": random.uniform(0.03, 0.06),
        }
        for _ in range(80)
    ]

def criar_snakes_pequenas():
    return [
        {
            "x": random.randint(-80, LARGURA + 80),
            "y": random.randint(0, ALTURA),
            "vx": random.uniform(0.4, 1.0),
            "vy": random.uniform(-0.2, 0.2),
            "segmentos": [],
        }
        for _ in range(4)
    ]

def criar_cobra_fantasma():
    return {
        "x": random.randint(0, LARGURA),
        "y": random.randint(0, ALTURA),
        "vx": random.uniform(0.5, 1.2),
        "vy": random.uniform(-0.2, 0.2),
        "segmentos": [],
    }

def atualizar_fundo_animado(particulas, estrelas, snakes_pequenas, cobra_fantasma, tempo):
    tela.fill((6, 10, 12))

    for particula in particulas:
        particula["x"] += particula["vx"]
        particula["y"] += particula["vy"]

        if particula["x"] < -5 or particula["x"] > LARGURA + 5:
            particula["x"] = random.randint(0, LARGURA)
        if particula["y"] < -5 or particula["y"] > ALTURA + 5:
            particula["y"] = random.randint(0, ALTURA)

        pygame.draw.circle(
            tela,
            (95, 135, 100),
            (int(particula["x"]), int(particula["y"])),
            particula["tamanho"],
        )

    for estrela in estrelas:
        brilho = (math.sin(tempo * estrela["velocidade"] + estrela["fase"]) + 1) / 2
        alpha = int(70 + brilho * 185)
        superficie = pygame.Surface((estrela["tamanho"] * 3, estrela["tamanho"] * 3), pygame.SRCALPHA)
        pygame.draw.circle(
            superficie,
            (255, 255, 255, alpha),
            (int(estrela["tamanho"] * 1.5), int(estrela["tamanho"] * 1.5)),
            estrela["tamanho"],
        )
        tela.blit(superficie, (estrela["x"], estrela["y"]))

    for snake in snakes_pequenas:
        snake["x"] += snake["vx"]
        snake["y"] += snake["vy"]

        if snake["x"] < -80 or snake["x"] > LARGURA + 80:
            snake["x"] = random.randint(-80, LARGURA + 80)
            snake["y"] = random.randint(0, ALTURA)
            snake["vx"] = random.uniform(0.4, 1.0)
            snake["vy"] = random.uniform(-0.2, 0.2)
        if snake["y"] < 0 or snake["y"] > ALTURA:
            snake["vy"] *= -1

        snake["segmentos"].append((int(snake["x"]), int(snake["y"])))
        if len(snake["segmentos"]) > 8:
            snake["segmentos"].pop(0)

        for indice, (px, py) in enumerate(snake["segmentos"]):
            tamanho = 2 + (indice % 3)
            cor = (0, 90 + indice * 15, 0)
            pygame.draw.rect(tela, cor, (px, py, tamanho, tamanho))

    cobra_fantasma["x"] += cobra_fantasma["vx"]
    cobra_fantasma["y"] += cobra_fantasma["vy"]

    if cobra_fantasma["x"] < -100 or cobra_fantasma["x"] > LARGURA + 100:
        cobra_fantasma["x"] = random.randint(0, LARGURA)
        cobra_fantasma["vx"] = random.uniform(-1.2, 1.2)
    if cobra_fantasma["y"] < -100 or cobra_fantasma["y"] > ALTURA + 100:
        cobra_fantasma["y"] = random.randint(0, ALTURA)
        cobra_fantasma["vy"] = random.uniform(-0.2, 0.2)

    cobra_fantasma["segmentos"].append((int(cobra_fantasma["x"]), int(cobra_fantasma["y"])))
    if len(cobra_fantasma["segmentos"]) > 18:
        cobra_fantasma["segmentos"].pop(0)

    if len(cobra_fantasma["segmentos"]) > 1:
        for indice, (px, py) in enumerate(cobra_fantasma["segmentos"]):
            if indice == len(cobra_fantasma["segmentos"]) - 1:
                continue
            proximo_x, proximo_y = cobra_fantasma["segmentos"][indice + 1]
            pygame.draw.line(tela, (70, 120, 70), (px, py), (proximo_x, proximo_y), 2)

def desenhar_texto(texto, tamanho, cor, x, y):
    # Função simples para desenhar texto na tela
    fonte = pygame.font.SysFont(None, tamanho)
    render = fonte.render(texto, True, cor)
    tela.blit(render, (x, y))

def carregar_recordes():
    # Carrega os recordes salvos em arquivo JSON
    if not os.path.exists(ARQUIVO_RECORDES):
        return []

    try:
        with open(ARQUIVO_RECORDES, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
    except (json.JSONDecodeError, OSError):
        return []

    return []

def salvar_recordes(recordes):
    # Salva a lista de recordes no arquivo
    with open(ARQUIVO_RECORDES, "w", encoding="utf-8") as arquivo:
        json.dump(recordes, arquivo, ensure_ascii=False, indent=2)
def carregar_perfis():
    # Carrega os perfis salvos para o jogador poder escolher um nome ja existente
    if not os.path.exists(ARQUIVO_PERFIS):
        return []

    try:
        with open(ARQUIVO_PERFIS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            if isinstance(dados, list):
                return [str(nome) for nome in dados if str(nome).strip()]
    except (json.JSONDecodeError, OSError):
        return []

    return []

def salvar_perfis(perfis):
    # Salva a lista de perfis no arquivo
    with open(ARQUIVO_PERFIS, "w", encoding="utf-8") as arquivo:
        json.dump(perfis, arquivo, ensure_ascii=False, indent=2)


def adicionar_perfil(nome, perfis):
    # Adiciona um novo perfil se o nome nao estiver na lista
    nome_limpo = nome.strip()
    if not nome_limpo:
        return perfis

    if nome_limpo not in perfis:
        perfis.append(nome_limpo)
        salvar_perfis(perfis)

    return perfis

def registrar_pontuacao(nome, pontos, recordes):
    # Registra a pontuação do jogador e mantem apenas os 5 melhores recordes
    novo_registro = {
        "nome": nome,
        "pontos": pontos,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    recordes.append(novo_registro)
    recordes_ordenados = sorted(recordes, key=lambda item: item["pontos"], reverse=True)[:MAX_RECORDES]
    salvar_recordes(recordes_ordenados)
    return recordes_ordenados

def obter_maior_recorde(recordes):
    # Retorna o maior recorde atual, para mostrar na tela durante o jogo
    return recordes[0] if recordes else None

def desenhar_menu_recordes(recordes):
    # Desenha a tela de recordes com os 5 melhores colocados
    desenhar_texto("TOP 5 RECORDES", 42, BRANCO, 170, 70)
    desenhar_texto("ESC - Voltar", 24, BRANCO, 210, 530)

    if not recordes:
        desenhar_texto("Nenhum recorde ainda", 28, BRANCO, 160, 220)
        return

    for indice, registro in enumerate(recordes, start=1):
        linha = f"{indice}. {registro['nome']} - {registro['pontos']} pts"
        y = 160 + indice * 45
        desenhar_texto(linha, 28, BRANCO, 120, y)

def main():
    # Loop principal do jogo, controla todos os estados: menu, seleção de perfil, jogo e game over
    estado = MENU
    snake = Snake()
    food = Food()
    pontos = 0
    som_tocado = False
    nome_jogador = ""
    nome_digitado = ""
    recordes = carregar_recordes()
    perfis = carregar_perfis()
    menu_index = 0
    perfil_index = 0
    game_over_index = 0
    estado_anterior = MENU
    particulas = criar_particulas()
    estrelas = criar_estrelas()
    snakes_pequenas = criar_snakes_pequenas()
    cobra_fantasma = criar_cobra_fantasma()

    while True:
        mudou_direcao = False

        for event in pygame.event.get():
            # Captura os eventos de teclado e mouse/fechar janela
            if event.type == pygame.QUIT:
                sair = datetime.now()
                print(f"Jogo finalizado às: {sair.strftime('%H:%M:%S')}")
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if estado == MENU:
                    # Menu inicial navegavel por setas, com opções de jogar, recordes e sair
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_index = (menu_index - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_index = (menu_index + 1) % 3
                    elif event.key in (pygame.K_SPACE, pygame.K_KP_ENTER, pygame.K_RETURN):
                        if menu_index == 0:
                            if perfis:
                                perfil_index = 0
                                estado = SELECAO_PERFIL
                            else:
                                nome_digitado = ""
                                estado = ENTRANDO_NOME
                        elif menu_index == 1:
                            estado_anterior = MENU
                            estado = RECORDES
                        elif menu_index == 2:
                            pygame.quit()
                            sys.exit()
                    elif event.key == pygame.K_r:
                        estado = RECORDES

                elif estado == SELECAO_PERFIL:
                    # Tela para escolher um perfil ja salvo ou criar um novo
                    if event.key in (pygame.K_UP, pygame.K_w):
                        perfil_index = (perfil_index - 1) % (len(perfis) + 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        perfil_index = (perfil_index + 1) % (len(perfis) + 1)
                    elif event.key in (pygame.K_SPACE, pygame.K_KP_ENTER, pygame.K_RETURN):
                        if perfil_index < len(perfis):
                            nome_jogador = perfis[perfil_index]
                            nome_digitado = nome_jogador
                            snake = Snake()
                            food = Food()
                            pontos = 0
                            som_tocado = False
                            game_over_index = 0
                            estado = JOGANDO
                            canal_fundo.stop()
                            sounds.tocar_som(canal_fundo, sounds.som_fundo, loops=-1)
                        else:
                            nome_digitado = ""
                            estado = ENTRANDO_NOME
                    elif event.key == pygame.K_ESCAPE:
                        estado = MENU

                elif estado == ENTRANDO_NOME:
                    # Tela para digitar o nome do jogador quando ele criar um novo perfil
                    if event.key == pygame.K_BACKSPACE:
                        nome_digitado = nome_digitado[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        nome_jogador = nome_digitado.strip() or "Jogador"
                        perfis = adicionar_perfil(nome_jogador, perfis)
                        snake = Snake()
                        food = Food()
                        pontos = 0
                        som_tocado = False
                        game_over_index = 0
                        estado = JOGANDO
                        canal_fundo.stop()
                        sounds.tocar_som(canal_fundo, sounds.som_fundo, loops=-1)
                    elif event.key == pygame.K_ESCAPE:
                        nome_digitado = ""
                        estado = MENU if perfis else MENU
                    elif event.unicode and event.unicode.isprintable() and len(nome_digitado) < 12:
                        nome_digitado += event.unicode
                elif estado == JOGANDO:
                    # Controle da cobra e da comida enquanto o jogo esta rodando
                    if event.key in (pygame.K_UP, pygame.K_w) and snake.direcao != (0, TAMANHO_BLOCO) and not mudou_direcao:
                        snake.direcao = (0, -TAMANHO_BLOCO)
                        mudou_direcao = True
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and snake.direcao != (0, -TAMANHO_BLOCO) and not mudou_direcao:
                        snake.direcao = (0, TAMANHO_BLOCO)
                        mudou_direcao = True
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and snake.direcao != (TAMANHO_BLOCO, 0) and not mudou_direcao:
                        snake.direcao = (-TAMANHO_BLOCO, 0)
                        mudou_direcao = True
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and snake.direcao != (-TAMANHO_BLOCO, 0) and not mudou_direcao:
                        snake.direcao = (TAMANHO_BLOCO, 0)
                        mudou_direcao = True
                    elif event.key == pygame.K_ESCAPE:
                        estado = MENU
                        canal_fundo.stop()
                        snake = Snake()
                        food = Food()
                        pontos = 0
                        som_tocado = False

                elif estado == GAME_OVER:
                    # Menu de morte, com opções para reiniciar, ver recordes ou voltar ao menu
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game_over_index = (game_over_index - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game_over_index = (game_over_index + 1) % 3
                    elif event.key in (pygame.K_SPACE, pygame.K_KP_ENTER, pygame.K_RETURN):
                        if game_over_index == 0:
                            estado = JOGANDO
                            snake = Snake()
                            food = Food()
                            pontos = 0
                            som_tocado = False
                            canal_fundo.stop()
                            sounds.tocar_som(canal_fundo, sounds.som_fundo, loops=-1)
                        elif game_over_index == 1:
                            estado_anterior = GAME_OVER
                            estado = RECORDES
                        else:
                            estado = MENU
                            snake = Snake()
                            food = Food()
                            pontos = 0
                            som_tocado = False
                    elif event.key == pygame.K_ESCAPE:
                        estado = MENU
                        snake = Snake()
                        food = Food()
                        pontos = 0
                        som_tocado = False
                        game_over_index = 0
                    elif event.key == pygame.K_r:
                        estado_anterior = GAME_OVER
                        estado = RECORDES

                elif estado == RECORDES:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        estado = estado_anterior if estado_anterior else MENU
        atualizar_fundo_animado(particulas, estrelas, snakes_pequenas, cobra_fantasma, pygame.time.get_ticks() / 1000)

        if estado == MENU:
            titulo = pygame.font.SysFont(None, 50).render("S N A K E", True, BRANCO)
            tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 150))
            opcoes = ["JOGAR", "RECORDES", "SAIR"]
            for indice, texto in enumerate(opcoes):
                cor = VERDE if indice == menu_index else BRANCO
                y = 250 + indice * 50
                desenhar_texto(f"> {texto}" if indice == menu_index else texto, 30, cor, 20, y)

            if (pygame.time.get_ticks() // 700) % 2 == 0:
                desenhar_texto("[SETAS] Navegar   [ENTER/ESPAÇO] Selecionar", 24, BRANCO, 18, 530)

        elif estado == SELECAO_PERFIL:
            desenhar_texto("SELECIONE O PERFIL", 40, BRANCO, 120, 120)
            if perfis:
                for indice, perfil in enumerate(perfis):
                    cor = VERDE if indice == perfil_index else BRANCO
                    desenhar_texto(f"> {perfil}" if indice == perfil_index else perfil, 30, cor, 180, 200 + indice * 45)
                desenhar_texto(f"> NOVO PERFIL" if perfil_index == len(perfis) else "NOVO PERFIL", 30, VERDE if perfil_index == len(perfis) else BRANCO, 180, 200 + len(perfis) * 45)
            else:
                desenhar_texto("Nenhum perfil salvo", 28, BRANCO, 170, 220)
            desenhar_texto("[SETAS] Navegar   [ENTER/ESPAÇO] Selecionar", 24, BRANCO, 120, 500)
            desenhar_texto("[ESC] Voltar", 24, BRANCO, 220, 535)

        elif estado == ENTRANDO_NOME:
            desenhar_texto("DIGITE SEU NOME", 40, BRANCO, 140, 180)
            desenhar_texto(nome_digitado or "_", 32, BRANCO, 220, 250)
            desenhar_texto("ENTER - CONFIRMAR", 26, BRANCO, 170, 330)
            desenhar_texto("ESC - VOLTAR", 24, BRANCO, 210, 380)

        elif estado == JOGANDO:
            snake.mover()

            if snake.corpo[0] == food.posicao:
                snake.crescer()
                food.posicao = food.gerar_posicao(snake.corpo)
                pontos += 1
                sounds.tocar_som(canal_comer, sounds.som_comer)

            x, y = snake.corpo[0]
            if x < 0 or x >= LARGURA or y < 0 or y >= ALTURA:
                recordes = registrar_pontuacao(nome_jogador, pontos, recordes)
                game_over_index = 0
                estado = GAME_OVER
                som_tocado = False
                canal_fundo.stop()
                sounds.tocar_som(canal_death, sounds.som_game_over)

            cabeca = snake.corpo[0]
            corpo_sem_cabeca = snake.corpo[1:]
            if cabeca in corpo_sem_cabeca:
                recordes = registrar_pontuacao(nome_jogador, pontos, recordes)
                game_over_index = 0
                estado = GAME_OVER
                som_tocado = False
                canal_fundo.stop()
                sounds.tocar_som(canal_death, sounds.som_game_over)

            snake.desenhar(tela)
            food.desenhar(tela)
            desenhar_texto(f"Pontos: {pontos}", 30, BRANCO, 10, 10)

            maior_recorde = obter_maior_recorde(recordes)
            if maior_recorde:
                texto_recorde = f"RECORDE: {maior_recorde['nome']} - {maior_recorde['pontos']} PONTOS"
                superficie = pygame.font.SysFont(None, 30).render(texto_recorde, True, BRANCO)
                x = LARGURA - superficie.get_width() - 10
                tela.blit(superficie, (x, 10))
        elif estado == GAME_OVER:
            if not som_tocado:
                sounds.tocar_som(canal_death, sounds.som_game_over)
                som_tocado = True
            largura_texto = 300
            x_titulo = (LARGURA - largura_texto) // 2
            desenhar_texto("GAME OVER", 50, BRANCO, x_titulo, 180)
            desenhar_texto(f"{nome_jogador}: {pontos} pontos", 30, BRANCO, 170, 250)

            opcoes_game_over = ["REINICIAR", "VER RECORDES", "VOLTAR AO MENU"]
            for indice, texto in enumerate(opcoes_game_over):
                cor = VERDE if indice == game_over_index else BRANCO
                y = 320 + indice * 50
                x_texto = 150
                if indice == game_over_index:
                    desenhar_texto(">", 30, VERDE, x_texto - 25, y)
                desenhar_texto(texto, 30, cor, x_texto, y)
            desenhar_texto("[SETAS] Navegar     [ENTER/ESPAÇO] Selecionar", 24, BRANCO, 145, 540)

        elif estado == RECORDES:
            desenhar_menu_recordes(recordes)
        pygame.display.update()
        relogio.tick(FPS)

if __name__ == "__main__":
    main()