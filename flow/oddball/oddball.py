from __future__ import annotations

from importlib.resources import files

import psychtoolbox as ptb
import zmq
from byte_triggers import MockTrigger, ParallelPortTrigger
from pynput import keyboard

from ..utils._checks import check_type, check_value
from ..utils.logs import logger
from ._config import (
    AUDIO_DEVICE,
    DURATION_ITI,
    DURATION_STIM,
    TRIGGER_ADDRESS,
    TRIGGERS,
)
from ._time import sleep
from ._utils import _load_sounds, parse_trial_list

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
    # prepare triggers
    trigger = MockTrigger() if mock else ParallelPortTrigger(TRIGGER_ADDRESS)
    # prepare fixation cross window
    input(">>> Press ENTER to start.")
    # main loop
    counter = 0
    hold = False
    while counter < len(trials):
        k, trial = trials[counter]
        # check for a message from Unity and potential hold
        socks = dict(poller.poll(timeout=10))
        if socket in socks and socks[socket] == zmq.POLLIN:
            hold = _read_message(socket, poller)
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
        trigger.signal(TRIGGERS.get(trial, TRIGGERS["novel"]))
        counter += 1
        # handle inter-trial period
        with keyboard.Listener(on_press=_callback_on_press):
            sleep(DURATION_ITI - DURATION_STIM)
    input(">>> Press ENTER to continue and close the window.")


def _callback_on_press(key):
    """Callback function to call when a key is pressed."""  # noqa: D401
    logger.info("Response %s pressed.", key)


def _read_message(socket) -> bool:
    """Check if we received a message from Unity."""
    message = socket.recv_string()  # Receive the message
    logger.info("Received message from Unity: %s", message)
    socket.send_string("ACK")
    return _MESSAGES.get(message)
