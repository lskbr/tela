import pygame
import os, sys
import socket
import time
from pygame.locals import *

#
# Globais
#

superficie = None
raio = None
largura = None
tamanho = None
servidor = None
endereco = "127.0.0.1", 8800
serv_backlog = 10
conexoes = []
recebido = b""
cor = (255, 0, 0)

# Cores
vermelho = (255, 0, 0)
azul = (0, 0, 255)
preto = (0, 0, 0)
branco = (255, 255, 255)
# Tamanho da grade: tgrade x tgrade
tgrade = 64
# Tamanho da Janela
xtam = 640
ytam = 640


def corrija(posicao_param):
    posicao = posicao_param

    posicao[0] = posicao[0] * largura - (raio - 1)
    posicao[1] = posicao[1] * largura - (raio - 1)
    return posicao


def linha(inicio, fim, cor):
    pass


def ponto(posicao, cor):
    global superficie
    pygame.draw.circle(superficie, cor, posicao, raio - 1)
    print("Ponto: %s Cor: %s" % (posicao, cor))
    pygame.display.update()


def coordenadas(dimensao):
    pass


def grade(dimensao):
    global largura, raio, tgrade
    largura = tamanho[0] / dimensao
    raio = largura / 2
    tgrade = dimensao
    for pedaco in range(dimensao):
        pygame.draw.line(
            superficie, azul, (pedaco * largura, 0), (pedaco * largura, tamanho[1])
        )
        pygame.draw.line(
            superficie, azul, (0, pedaco * largura), (tamanho[1], pedaco * largura)
        )
    pygame.display.update()


def inicialize():
    global superficie
    global raio
    global largura
    global tamanho
    pygame.init()
    info = pygame.display.Info()
    pygame.display.set_mode((xtam, ytam), 0, 16)
    superficie = pygame.display.get_surface()
    tamanho = superficie.get_size()
    print("Tamanho = %s Largura = %s Raio = %s" % (tamanho, largura, raio))


def inicialize_servidor():
    global servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(endereco)
    servidor.setblocking(0)
    servidor.listen(serv_backlog)


def processa_comando(comando, parametros):
    global cor
    if comando == b"PO":
        parametros[0] = int(parametros[0])
        parametros[1] = int(parametros[1])
        ponto(corrija(parametros), cor)
    if comando == b"PC":
        parametros[0] = int(parametros[0])
        parametros[1] = int(parametros[1])
        ponto(corrija([parametros[0], parametros[1]]), parametros[2])
    if comando == b"CL":
        superficie.fill(preto)
        tgrade = int(parametros[0])
        grade(tgrade)
    if comando == b"CO":
        cor = (int(parametros[0]), int(parametros[1]), int(parametros[2]))
        print(cor)


def verifica_dados():
    global conexoes
    global recebido
    try:
        for cc in conexoes:
            n = cc[0].recv(1024)
            if len(n) > 0:
                recebido += n
                print("Recebi: %s" % n)
                # aqui!!!
                while 1:
                    c = recebido.find(b"\n")
                    if c != -1:
                        linha = recebido[:c]
                        print("c=%d linha=%s" % (c, linha))
                        comando = linha[0:2]
                        parametros = linha[3:].split(b",")
                        print("Comando: %s Parametro: %s" % (comando, parametros))
                        processa_comando(comando, parametros)
                        recebido = recebido[c + 1 :]
                        print(
                            "tamanho do recebido: %d recebido: %s"
                            % (len(recebido), recebido)
                        )
                    else:
                        break
    except socket.error as erro:
        numero, nome = erro
        print("Erro: %d - %s" % (numero, nome))


def verifica_conexoes():
    global conexoes
    try:
        q, v = servidor.accept()
        print("Accept OK!")
        conexoes += [[q, v]]
        print(conexoes)
    except:
        q = None


# Programa Principal
inicialize()
inicialize_servidor()

grade(tgrade)
try:
    while 1:
        e = pygame.event.peek()
        if e:
            e = pygame.event.poll()
            if e.type == MOUSEBUTTONDOWN:
                print(conexoes)
            elif e.type == KEYDOWN and e.key == K_s:
                pygame.image.save(superficie, "tela.png")
            elif e.type == QUIT:
                raise SystemExit
        verifica_conexoes()
        if len(conexoes) > 0:
            verifica_dados()
        time.sleep(0.1)
finally:
    pygame.display.quit()
