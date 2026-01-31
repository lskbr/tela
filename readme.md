# Tela and Graficos.py

First version of code written in 2002 for Python 2.x.

It still very old, but it is running in Python >3.12.

The idea is to enhance the code and make it more Pythonic.
After +20 years unchanged, it needs some care.

Source: https://www.nilo.pro.br/python/index.html


# Installing

- You need Python 3.13
- uv is prefered, but if your pip already supports pyproject.toml, you are ready.

```
uv venv
uv pip install pyproject.toml
```


# Playing with

### Start tela.py

Tela is the drawing screen. It is a simple TCP/IP server that receive even simple commands in a socket. The code still very fragile, but it will enhanced over time. Tela means screen in Brazilian Portuguese.

```
python tela.py &
```

### Start graficos.py

Graficos has the commands needed to interact with tela.py. You can pass `--host` and `--port` to match your tela.py server, and optionally `--read-from FILE` to send commands from a file after connecting.

```
python graficos.py
python graficos.py --host 127.0.0.1 --port 8800
python graficos.py --read-from my_commands.txt
```

Then, start drawing:

```
>>> clear(20)       # Creates a 20x20 grid
>>> point(1, 1)     # Plots a dot at x=1, y=1
>>> color(255, 128, 1)  # Sets the color (red, green, blue) for next points
>>> print_points()  # Prints all previously sent commands
>>> save_commands() # Prompts for a file name and saves the command list
>>> load_commands() # Prompts for a file name and sends commands from that file
>>> load_commands("file.txt")  # Or pass the file name directly
```
