from __future__ import annotations

import click

from .. import set_log_level
from ..oddball import oddball


@click.command(name="oddball")
@click.option(
    "--condition",
    type=str,
    help="condition to run among main1 | main2 | main3 | solo | stp1 | stp2 | stp3.",
    prompt="Condition to run",
)
@click.option("--mock", help="run with a mock trigger.", is_flag=True)
def run(condition: str, mock: bool):
    """Run oddball() command."""
    set_log_level("INFO")
    oddball(condition, mock=mock)
