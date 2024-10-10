from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

from ..utils._checks import check_type, check_value, ensure_path
from ..utils._imports import import_optional_dependency
from ..utils.logs import logger
from ._utils import parse_trial_list

if TYPE_CHECKING:
    from psychopy.sound.backend_ptb import SoundPTB


_TRIAL_LIST_MAPPING = [
    elt.stem
    for elt in (files("flow.oddball") / "trialList").iterdir()
    if elt.is_file() and elt.suffix == ".txt"
]
_DURATION_STIM: float = 0.2  # seconds
_DURATION_ITI: float = 1.0  # seconds
_DURATION_FLICKERING: float = 0.05  # seconds
_TRIGGERS: dict[str, int] = {
    "standard": 1,
    "target": 2,
    "novel": 3,
}

# check the variables
check_type(_DURATION_STIM, ("numeric",), "_DURATION_STIM")
check_type(_DURATION_ITI, ("numeric",), "_DURATION_ITI")
check_type(_DURATION_FLICKERING, ("numeric",), "_DURATION_FLICKERING")
assert 0.3 < _DURATION_ITI - _DURATION_STIM - 0.2
assert all(elt in _TRIGGERS for elt in ("standard", "target", "novel"))


def oddball(condition: str, mock: bool = False) -> None:
    """Run the oddball paradigm.

    Parameters
    ----------
    condition : "main1" | "main2" | "main3" | "solo" | "stp1" | "stp2" | "stp3"
        Oddball condition to run.
    mock : bool
        If True, uses a MockTrigger instead of a ParallelPortTrigger.
    """
    import_optional_dependency("byte_triggers")
    import_optional_dependency("psychopy")
    import_optional_dependency("psychtoolbox")

    import psychtoolbox as ptb
    from byte_triggers import MockTrigger, ParallelPortTrigger
    from psychopy.core import wait

    check_type(condition, (str,), "condition")
    check_value(condition, _TRIAL_LIST_MAPPING, "condition")
    check_type(mock, (bool,), "mock")
    # load trials and sounds
    fname = files("flow.oddball") / "trialList" / f"{condition}.txt"
    trials = parse_trial_list(fname)
    sounds = _load_sounds(trials)
    # prepare triggers
    trigger = MockTrigger() if mock else ParallelPortTrigger(0x2FB8)
    # prepare fixation cross window
    input(">>> Press ENTER to start.")
    # main loop
    for k, trial in trials:
        logger.info("Trial %i / %i: %s", k, trials[-1][0], trial)
        # retrieve trigger value and sound
        if trial in _TRIGGERS:
            assert trial in ("standard", "target"), f"Error with trial ({k}, {trial})."
            value = _TRIGGERS[trial]
        else:
            assert trial.startswith("wav"), f"Error with trial ({k}, {trial})."
            value = _TRIGGERS["novel"]
        sound = sounds[trial]
        # schedule sound, wait, and deliver triggers simultanouesly with the sound
        sound.play(when=ptb.GetSecs() + _DURATION_STIM)
        wait(_DURATION_STIM, hogCPUperiod=_DURATION_STIM)
        trigger.signal(value)
        wait(_DURATION_ITI - _DURATION_STIM)
    input(">>> Press ENTER to continue and close the window.")


def _load_sounds(trials) -> dict[str, SoundPTB]:
    """Create psychopy sound objects."""
    from psychopy.sound.backend_ptb import SoundPTB

    sounds = dict()
    fname_standard = files("flow.oddball") / "sounds" / "low_tone-48000.wav"
    fname_standard = ensure_path(fname_standard, must_exist=True)
    sounds["standard"] = SoundPTB(
        fname_standard, secs=_DURATION_STIM, hamming=True, name="stim", sampleRate=48000
    )
    fname_target = files("flow.oddball") / "sounds" / "high_tone-48000.wav"
    fname_target = ensure_path(fname_target, must_exist=True)
    sounds["target"] = SoundPTB(
        fname_target, secs=_DURATION_STIM, hamming=True, name="stim", sampleRate=48000
    )

    novels = [trial[1] for trial in trials if trial[1].startswith("wav")]
    for novel in novels:
        fname = files("flow.oddball") / "sounds" / f"{novel}-48000.wav"
        sounds[novel] = SoundPTB(
            fname, secs=_DURATION_STIM, hamming=True, name="stim", sampleRate=48000
        )
    return sounds
