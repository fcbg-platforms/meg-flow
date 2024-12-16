from ..utils._checks import check_type

DURATION_STIM: float = 0.2  # seconds
DURATION_ITI: float = 1.0  # seconds
TRIGGER_ADDRESS: int | str = 0x2FB8  # 0x2FB8 or /dev/parport0
TRIGGERS: dict[str, int] = {
    "standard": 1,
    "target": 2,
    "novel": 3,
    "hold": 4,
}
AUDIO_DEVICE: str = "Speakers (SPL Crimson 2.9.86.25)"
AUDIO_VOLUME: float = 0.1

# check the variables
check_type(DURATION_STIM, ("numeric",), "DURATION_STIM")
check_type(DURATION_ITI, ("numeric",), "DURATION_ITI")
assert 0.3 < DURATION_ITI - DURATION_STIM - 0.2
assert all(elt in TRIGGERS for elt in ("standard", "target", "novel"))
