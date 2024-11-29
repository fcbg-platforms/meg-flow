from __future__ import annotations

import time
from importlib.resources import files

import zmq
from psychopy.hardware.keyboard import Keyboard

from ..utils._checks import check_type, check_value
from ..utils._imports import import_optional_dependency
from ..utils.logs import logger, warn
from ._config import (
    AUDIO_DEVICE,
    DURATION_ITI,
    DURATION_STIM,
    TRIGGER_ADDRESS,
    TRIGGERS,
)
from ._time import Clock, sleep
from ._utils import _disable_psychopy_logs, _load_sounds, parse_trial_list

_MESSAGES: dict[str, bool] = {"hold": True, "continue": False}
_TRIAL_LIST_MAPPING: list[str] = [
    elt.stem
    for elt in (files("flow.oddball") / "trialList").iterdir()
    if elt.is_file() and elt.suffix == ".txt"
]


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

    check_type(condition, (str,), "condition")
    check_value(condition, _TRIAL_LIST_MAPPING, "condition")
    check_type(mock, (bool,), "mock")
    # create the ZeroMQ context and a subscriber socket to receive messages from Unity
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP: Server side for REQ/REP pattern
    socket.bind("tcp://localhost:5555")  # Bind to port 5555
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    # load trials and sounds
    fname = files("flow.oddball") / "trialList" / f"{condition}.txt"
    trials = parse_trial_list(fname)
    sounds = _load_sounds(trials, DURATION_STIM, AUDIO_DEVICE)
    # prepare triggers and keyboard
    trigger = MockTrigger() if mock else ParallelPortTrigger(TRIGGER_ADDRESS)
    keyboard = Keyboard()
    with _disable_psychopy_logs():
        keyboard.stop()
    # prepare fixation cross window
    input(">>> Press ENTER to start.")
    # main loop
    counter = 0
    while counter < len(trials):
        k, trial = trials[counter]
        # check for a message from Unity and potential hold
        hold = _check_message_for_hold(socket, poller)
        if hold:
            logger.info("Holding at trial %i / %i", k, trials[-1][0])
            sounds["standard"].play(when=ptb.GetSecs() + DURATION_STIM)
            sleep(DURATION_STIM)
            trigger.signal(TRIGGERS["hold"])
            sleep(DURATION_ITI - DURATION_STIM)
            continue
        logger.info("Trial %i / %i: %s", k, trials[-1][0], trial)
        # handle trigger and sound
        sounds[trial].play(when=ptb.GetSecs() + DURATION_STIM)
        sleep(DURATION_STIM)
        trigger.signal(TRIGGERS[trial if trial in TRIGGERS else "novel"])
        counter += 1
        if trial in TRIGGERS:  # sanity-check the trial and handle inter-trial sleep
            assert trial in ("standard", "target"), f"Error with trial ({k}, {trial})."
            sleep(DURATION_ITI - DURATION_STIM)
        else:
            assert trial.startswith("wav"), f"Error with trial ({k}, {trial})."
            _sleep_and_monitor_keyboard(DURATION_ITI - DURATION_STIM, keyboard)
    input(">>> Press ENTER to continue and close the window.")


def _check_message_for_hold(socket, poller) -> bool:
    """Check if we received a message from Unity."""
    socks = dict(poller.poll(timeout=10))
    if socket in socks and socks[socket] == zmq.POLLIN:
        message = socket.recv_string()  # Receive the message
        logger.info("Received message from Unity: %s", message)
        socket.send_string("ACK")
        hold = _MESSAGES.get(message)
    else:
        hold = False
    return hold


def _sleep_and_monitor_keyboard(duration: float, keyboard: Keyboard) -> None:
    """Sleep and monitor the keyboard."""
    clock = Clock()
    keyboard.start()
    duration *= 1e9
    while True:
        remaining_time = duration - clock.get_time_ns()  # nanoseconds
        if remaining_time <= 0:
            break
        keys = keyboard.getKeys(keyList=["0"], waitRelease=True)
        if len(keys) > 1:
            warn("Multiple space key pressed simultaneously. Skipping.")
            continue
        elif len(keys) == 1:
            logger.info("Response '0' received.")
        if remaining_time >= 200000:  # 200 microseconds
            time.sleep(remaining_time * 1e-9 / 2)
    with _disable_psychopy_logs():
        keyboard.stop()
