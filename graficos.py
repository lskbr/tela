"""
Client for the Tela drawing server. Sends commands PO, CO, CL over TCP.
"""

import code
import socket

import click

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8800

# Module-level connection for interactive use; set by initialize() or main()
_connection: "TelaConnection | None" = None


class TelaConnection:
    """Manages socket connection to the Tela server and command history."""

    def __init__(self) -> None:
        self._socket: socket.socket | None = None
        self._host: str = ""
        self._port: int = 0
        self._connected = False
        self._commands: list[bytes] = []

    @property
    def is_connected(self) -> bool:
        return self._connected and self._socket is not None

    def connect(self, host: str, port: int) -> None:
        """Connect to the Tela server. Raises OSError on failure."""
        self.close()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._socket.connect((host, port))
        except OSError:
            self._socket = None
            raise
        self._host = host
        self._port = port
        self._connected = True
        print("OK! Initialized.")

    def send(self, data: bytes) -> None:
        """Send data to the server. Raises ConnectionError if not connected or send fails."""
        if not self.is_connected or self._socket is None:
            raise ConnectionError(
                "Not connected to server; call initialize(host, port) first"
            )
        try:
            self._socket.send(data)
        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            raise ConnectionError(
                "Send failed: server unreachable or connection closed"
            ) from e

    def close(self) -> None:
        """Close the connection and clear command history."""
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
        self._connected = False
        self._commands = []


def _get_connection() -> TelaConnection:
    """Return the module-level connection; raise if never initialized."""
    if _connection is None:
        raise ConnectionError(
            "Not connected to server; call initialize(host, port) first"
        )
    return _connection


def initialize(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Connect to the Tela server at the given host and port."""
    global _connection
    _connection = TelaConnection()
    _connection.connect(host, port)


def point(x: int, y: int) -> None:
    """Send a point command (PO) at grid coordinates (x, y)."""
    conn = _get_connection()
    cmd = b"PO %d,%d\n" % (x, y)
    conn._commands.append(cmd)
    conn.send(cmd)


def color(red: int, green: int, blue: int) -> None:
    """Set the drawing color (CO) for subsequent points."""
    conn = _get_connection()
    cmd = b"CO %d,%d,%d\n" % (red, green, blue)
    conn._commands.append(cmd)
    conn.send(cmd)


def clear(grid_size: int = 16) -> None:
    """Clear the screen and draw a new grid of dimension grid_size x grid_size (CL)."""
    conn = _get_connection()
    conn.send(b"CL %d\n" % grid_size)
    conn._commands = []


def print_points() -> None:
    """Print all commands sent since the last clear."""
    conn = _get_connection()
    for cmd in conn._commands:
        print(cmd)


def save_commands() -> None:
    """Prompt for a file name and save the current command list to that file."""
    conn = _get_connection()
    path = input("File name to save commands: ").strip()
    if not path:
        return
    with open(path, "wb") as f:
        for cmd in conn._commands:
            f.write(cmd)


def load_commands(filename: str | None = None) -> None:
    """Read commands from a file and send them to the server. If filename is None, prompt for it."""
    conn = _get_connection()
    if filename is None:
        filename = input("File name to read commands from: ").strip()
    if not filename:
        return
    with open(filename, "rb") as f:
        for line in f:
            line = line.rstrip(b"\n")
            if not line or len(line) < 3:
                continue
            # Ensure newline for server
            if not line.endswith(b"\n"):
                line = line + b"\n"
            conn._commands.append(line)
            conn.send(line)


def close() -> None:
    """Close the connection to the Tela server."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


@click.command()
@click.option(
    "--host",
    default=DEFAULT_HOST,
    help="Tela server host.",
)
@click.option(
    "--port",
    default=DEFAULT_PORT,
    type=int,
    help="Tela server port.",
)
@click.option(
    "--read-from",
    "read_from",
    type=click.Path(exists=True, path_type=str),
    default=None,
    help="Read commands from this file and send them after connecting.",
)
def main(host: str, port: int, read_from: str | None) -> None:
    """Run the graficos client; connect to Tela and optionally run commands from a file."""
    global _connection
    _connection = TelaConnection()
    try:
        _connection.connect(host, port)
    except OSError as e:
        raise SystemExit(f"Could not connect to {host}:{port}: {e}") from e

    if read_from is not None:
        with open(read_from, "rb") as f:
            for line in f:
                line = line.rstrip(b"\n")
                if not line or len(line) < 3:
                    continue
                if not line.endswith(b"\n"):
                    line = line + b"\n"
                _connection._commands.append(line)
                _connection.send(line)

    # Drop into interactive REPL so point(), color(), clear(), etc. are available
    code.interact(
        local={
            "initialize": initialize,
            "point": point,
            "color": color,
            "clear": clear,
            "print_points": print_points,
            "save_commands": save_commands,
            "load_commands": load_commands,
            "close": close,
        }
    )


if __name__ == "__main__":
    main()
