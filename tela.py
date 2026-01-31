"""
Tela: TCP server that draws on a pygame grid. Accepts commands PO, PC, CL, CO.
"""
import asyncio
import logging

import click
import pygame
from pygame.locals import KEYDOWN, K_s, MOUSEBUTTONDOWN, QUIT

# Color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class TelaApp:
    """Application state and protocol handler. No globals."""

    def __init__(self, host, port, grid_size, window_width, window_height, title):
        self.host = host
        self.port = port
        self.grid_size = grid_size
        self.window_width = window_width
        self.window_height = window_height
        self.title = title
        # Pygame state (set in _init_pygame)
        self.surface = None
        self.size = None
        self.cell_width = None
        self.radius = None
        self.color = RED
        self._server = None
        self._running = True

    def adjust_position(self, position):
        """Convert grid coordinates to pixel coordinates."""
        pos = list(position)
        pos[0] = pos[0] * self.cell_width - (self.radius - 1)
        pos[1] = pos[1] * self.cell_width - (self.radius - 1)
        return pos

    def line(self, start, end, color):
        """Draw a line (stub)."""
        pass

    def draw_point(self, position, color):
        """Draw a circle at the given pixel position."""
        pygame.draw.circle(
            self.surface, color, position, self.radius - 1
        )
        logging.debug("Point: %s Color: %s", position, color)
        pygame.display.update()

    def coordinates(self, dimension):
        """Coordinates helper (stub)."""
        pass

    def draw_grid(self, dimension):
        """Draw grid of dimension x dimension."""
        self.cell_width = self.size[0] / dimension
        self.radius = self.cell_width / 2
        self.grid_size = dimension
        for i in range(dimension):
            pygame.draw.line(
                self.surface,
                BLUE,
                (i * self.cell_width, 0),
                (i * self.cell_width, self.size[1]),
            )
            pygame.draw.line(
                self.surface,
                BLUE,
                (0, i * self.cell_width),
                (self.size[0], i * self.cell_width),
            )
        pygame.display.update()

    def _init_pygame(self):
        """Initialize pygame and the main window."""
        pygame.init()
        pygame.display.set_mode((self.window_width, self.window_height), 0, 16)
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.get_surface()
        self.size = self.surface.get_size()
        logging.debug(
            "Size = %s cell_width = %s radius = %s",
            self.size,
            self.cell_width,
            self.radius,
        )

    def process_command(self, command, params):
        """Handle one wire command: PO, PC, CL, CO."""
        if command == b"PO":
            params[0] = int(params[0])
            params[1] = int(params[1])
            self.draw_point(self.adjust_position(params), self.color)
        if command == b"PC":
            params[0] = int(params[0])
            params[1] = int(params[1])
            color = (int(params[2]), int(params[3]), int(params[4]))
            self.draw_point(
                self.adjust_position([params[0], params[1]]),
                color,
            )
        if command == b"CL":
            self.surface.fill(BLACK)
            self.grid_size = int(params[0])
            self.draw_grid(self.grid_size)
        if command == b"CO":
            self.color = (
                int(params[0]),
                int(params[1]),
                int(params[2]),
            )
            logging.debug("Color set: %s", self.color)

    async def _handle_client(self, reader, writer):
        """Read newline-delimited lines and dispatch to process_command."""
        addr = writer.get_extra_info("peername")
        logging.info("Client connected: %s", addr)
        try:
            while self._running:
                line = await reader.readuntil(b"\n")
                line = line.rstrip(b"\n")
                if not line or len(line) < 3:
                    continue
                cmd = line[0:2]
                param_str = line[3:]
                params = [p.strip() for p in param_str.split(b",")]
                logging.debug("Command: %s Params: %s", cmd, params)
                self.process_command(cmd, params)
        except asyncio.IncompleteReadError:
            pass
        except Exception as e:
            logging.exception("Error handling client %s: %s", addr, e)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            logging.info("Client disconnected: %s", addr)

    async def _game_loop(self):
        """Poll pygame events and yield to the event loop."""
        while self._running:
            if pygame.event.peek():
                event = pygame.event.poll()
                if event.type == MOUSEBUTTONDOWN:
                    logging.debug("Mouse click")
                elif event.type == KEYDOWN and event.key == K_s:
                    pygame.image.save(self.surface, "tela.png")
                elif event.type == QUIT:
                    self._running = False
                    return
            await asyncio.sleep(0.01)

    async def run(self):
        """Initialize pygame, start async server, and run game loop until quit."""
        self._init_pygame()
        self.draw_grid(self.grid_size)

        self._server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port,
        )
        addr = self._server.sockets[0].getsockname()
        logging.info("Server listening on %s:%s", addr[0], addr[1])

        try:
            async with self._server:
                server_task = asyncio.create_task(self._server.serve_forever())
                try:
                    await self._game_loop()
                finally:
                    server_task.cancel()
                    try:
                        await server_task
                    except asyncio.CancelledError:
                        pass
        finally:
            if self._server:
                self._server.close()
                await self._server.wait_closed()
            pygame.display.quit()


@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Bind address.",
)
@click.option(
    "--port",
    default=8800,
    type=int,
    help="Bind port.",
)
@click.option(
    "--grid-size",
    default=64,
    type=int,
    help="Grid dimension (N x N).",
)
@click.option(
    "--width",
    default=640,
    type=int,
    help="Window width in pixels.",
)
@click.option(
    "--height",
    default=640,
    type=int,
    help="Window height in pixels.",
)
@click.option(
    "--title",
    default="Tela",
    help="Window title.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable debug logging.",
)
def main(host, port, grid_size, width, height, title, verbose):
    """Run the Tela drawing server."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    app = TelaApp(host, port, grid_size, width, height, title)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
