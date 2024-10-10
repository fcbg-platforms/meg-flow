from __future__ import annotations

import click


@click.command(name="forward-force")
@click.option(
    "--ip", help="IP address of the Unity server.", default="127.0.0.1", type=str
)
@click.option("--port", help="Port of the Unity server.", default=8055, type=int)
def run(ip: str, port: int) -> None:
    """Run forward_force() command."""
