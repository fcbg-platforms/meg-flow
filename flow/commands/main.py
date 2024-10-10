from __future__ import annotations

import click

from .forward_force import run as forward_force
from .oddball import run as oddball
from .sys_info import run as sys_info


@click.group()
def run() -> None:
    """Main package entry-point."""  # noqa: D401


run.add_command(forward_force)
run.add_command(oddball)
run.add_command(sys_info)
