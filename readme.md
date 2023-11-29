# Tela and Graficos.py

First version of code written in 2002 for Python 2.x.

It still very old, but it is running in Python 3.12.

The idea is to enhance the code and make it more Pythonic.
After +20 years unchanged, it needs some care.

Source: https://www.nilo.pro.br/python/index.html


# Installing

- You need Python 3.12
- Poetry is prefered, but if your pip already supports pyproject.toml, you are ready.

```
poetry install
poetry shell
```


# Playing with

### Start tela.py

Tela is the drawing screen. It is a simple TCP/IP server that receive even simples commands in a socket. The code still very fragile, but it will enhanced over time. Tela means screen in Brazilian Portuguese.

```
python tela.py &
```

### Start graficos.py

Graficos has the commands needed to interact with tela.py

```
python -i graficos.py
```

Then, start drawing:

```
>>> limpa(20, 20)  # Creates a 20x20 grid
>>> ponto(1,1) # Plots a dot at x=1, y=1
>>> cor(255,128,1) # Sets the color of next dot to red=255, green=128 and blue=1
>>> imprima_pontos()  # prints all previously sent commands
```
