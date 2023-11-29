import os
import socket


IP_TELA = "127.0.0.1"
PORTA_TELA = 8800

s = None
comandos = []


def inicializa(ip=IP_TELA, porta=PORTA_TELA):
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, porta))
    except socket.error as erro:
        numero, nome = erro
        print("Erro: %d - %s" % (numero, nome))
    else:
        print("OK! Inicializado.")


def ponto(x, y):
    comando = b"PO %d,%d\n" % (x, y)
    comandos.append(comando)
    s.send(comando)


def cor(vermelho, verde, azul):
    comando = b"CO %d,%d,%d\n" % (vermelho, verde, azul)
    comandos.append(comando)
    s.send(comando)


def limpa(a=16):
    global comandos
    s.send(b"CL %d,%d\n" % (a, a))
    comandos = []


def imprima_pontos():
    for a in comandos:
        print(a)


def finaliza():
    s.close()


if __name__ == "__main__":
    inicializa()
