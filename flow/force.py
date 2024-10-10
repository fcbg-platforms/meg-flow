from __future__ import annotations

import multiprocessing as mp
import socket as sc
import time

from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput

_GAIN: float = 266.643
_GRAVITY_CONSTANT: float = 9.806
_OFFSET: float = 0.0065339


def forward_force(ip: str, port: int, status: mp.managers.ValueProxy) -> None:
    """Forward the force measurement to Unity via socket."""
    socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)

    def _callback_on_voltage_ratio_change(self, voltageRatio) -> None:
        currentWeight = (voltageRatio - _OFFSET) * _GAIN
        currentForce = currentWeight * _GRAVITY_CONSTANT
        socket.sendto(bytes(str(currentForce), encoding="ascii"), (ip, port))

    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput0.setOnVoltageRatioChangeHandler(_callback_on_voltage_ratio_change)
    voltageRatioInput0.openWaitForAttachment(500)
    voltageRatioInput0.setDataInterval(10)
    status.value = 1
    while status.value == 1:
        time.sleep(0.1)
    voltageRatioInput0.close()
