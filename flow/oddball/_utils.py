from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

from psychopy import logging

from ..utils._checks import check_value, ensure_path
from ..utils.logs import logger, warn

if TYPE_CHECKING:
    from pathlib import Path

    from psychopy.sound.backend_ptb import SoundPTB


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


def _load_sounds(
    trials: list[tuple[int, str]], duration: float, device: str, volume: float
) -> dict[str, SoundPTB]:
    """Create psychopy sound objects."""
    from psychopy.sound import setDevice

    setDevice(device, kind="output")

    from psychopy.sound.backend_ptb import SoundPTB

    sounds = dict()
    fname_standard = files("flow.oddball") / "sounds" / "low_tone-48000.wav"
    fname_standard = ensure_path(fname_standard, must_exist=True)
    sounds["standard"] = SoundPTB(
        fname_standard, secs=duration, hamming=True, name="stim", sampleRate=48000
    )
    sounds["standard"].setVolume(volume)
    fname_target = files("flow.oddball") / "sounds" / "high_tone-48000.wav"
    fname_target = ensure_path(fname_target, must_exist=True)
    sounds["target"] = SoundPTB(
        fname_target, secs=duration, hamming=True, name="stim", sampleRate=48000
    )
    sounds["target"].setVolume(volume)
    novels = [trial[1] for trial in trials if trial[1].startswith("wav")]
    for novel in novels:
        fname = files("flow.oddball") / "sounds" / f"{novel}-48000.wav"
        sounds[novel] = SoundPTB(
            fname, secs=duration, hamming=True, name="stim", sampleRate=48000
        )
        sounds[novel].setVolume(volume)
    return sounds


class _disable_psychopy_logs:
    def __enter__(self) -> None:
        logging.console.setLevel(logging.CRITICAL)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        logging.console.setLevel(logging.WARNING)
