from __future__ import annotations

from importlib.resources import files

import zmq

from ..utils._checks import check_type, check_value
from ..utils._imports import import_optional_dependency
from ..utils.logs import logger
from ._config import (
    AUDIO_DEVICE,
    DURATION_ITI,
    DURATION_STIM,
    TRIGGER_ADDRESS,
    TRIGGERS,
)
from ._utils import _load_sounds, parse_trial_list

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
    from psychopy.core import wait

    check_type(condition, (str,), "condition")
    check_value(condition, _TRIAL_LIST_MAPPING, "condition")
    check_type(mock, (bool,), "mock")
    # create the ZeroMQ context and a subscriber socket to receive messages from Unity
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP: Server side for REQ/REP pattern
    socket.bind("tcp://localhost:5555")  # Bind to port 5555
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    hold = False
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
    while counter < len(trials):
        k, trial = trials[counter]
        # check for messages from Unity
        socks = dict(poller.poll(timeout=10))
        if socket in socks and socks[socket] == zmq.POLLIN:
            message = socket.recv_string()  # Receive the message
            logger.info("Received message from Unity: %s", message)
            socket.send_string("ACK")
            if message == "hold":
                hold = True
            elif message == "continue":
                hold = False
        if hold:
            logger.info("Holding at trial %i / %i", k, trials[-1][0])
            sounds["standard"].play(when=ptb.GetSecs() + DURATION_STIM)
            wait(DURATION_STIM, hogCPUperiod=DURATION_STIM)
            trigger.signal(TRIGGERS["hold"])
            wait(DURATION_ITI - DURATION_STIM)
            continue
        logger.info("Trial %i / %i: %s", k, trials[-1][0], trial)
        # retrieve trigger value and sound
        if trial in TRIGGERS:
            assert trial in ("standard", "target"), f"Error with trial ({k}, {trial})."
            value = TRIGGERS[trial]
        else:
            assert trial.startswith("wav"), f"Error with trial ({k}, {trial})."
            value = TRIGGERS["novel"]
        sound = sounds[trial]
        # schedule sound, wait, and deliver triggers simultanouesly with the sound
        sound.play(when=ptb.GetSecs() + DURATION_STIM)
        wait(DURATION_STIM, hogCPUperiod=_URATION_STIM)
        trigger.signal(value)
        counter += 1
        wait(DURATION_ITI - DURATION_STIM)
    input(">>> Press ENTER to continue and close the window.")
