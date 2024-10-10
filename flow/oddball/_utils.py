from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

from ..utils._checks import check_value
from ..utils.logs import logger, warn

if TYPE_CHECKING:
    from pathlib import Path


def list_novel_sounds() -> list[str]:
    """List the available sounds."""
    novel_sounds = list()
    for file in (files("flow.oddball") / "sounds").iterdir():
        if file.suffix != ".wav":
            warn(f"Non-wav file {file} found in the sounds directory.")
            continue
        if file.name.startswith("wav"):
            novel_sounds.append(file.name)
    return novel_sounds


def parse_trial_list(fname: Path) -> list[tuple[int, str]]:
    """Parse the trialList file."""
    logger.info("Loading trial list %s", fname.name)
    with open(fname) as f:
        lines = f.readlines()
    lines = [line.rstrip("\n").split(", ") for line in lines if len(line) != 0]
    novel_sounds = [sound.split("-")[0] for sound in list_novel_sounds()]
    lines_checked = list()
    expected_idx = 1
    for line in lines:
        try:
            idx = int(line[0])
        except ValueError:
            raise ValueError(
                f"The trial idx {line[0]} could not be interpreted as an integer."
            )
        if expected_idx != idx:
            raise ValueError(
                f"The trial idx {idx} does not match the expected idx {expected_idx}."
            )
        trial = line[1]
        if not trial.startswith("wav"):
            check_value(trial, ("standard", "target", "cross"), "trial")
        else:
            check_value(trial, novel_sounds, "trial")
        if trial != "cross":
            expected_idx += 1
        lines_checked.append((idx, trial))
    return lines_checked
