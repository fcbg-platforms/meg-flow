from __future__ import annotations

import socket as sc

import click
from Phidget22.Devices.VoltageRatioInput import VoltageRatioInput

_GAIN: float = 262.36
_GRAVITY_CONSTANT: float = 9.806
_OFFSET: float = 0.0092264


@click.command(name="forward-force")
@click.option(
    "--ip", help="IP address of the Unity server.", default="127.0.0.1", type=str
)
@click.option("--port", help="Port of the Unity server.", default=8055, type=int)
def run(ip: str, port: int) -> None:
    """Run forward_force() command."""
    socket = sc.socket(sc.AF_INET, sc.SOCK_DGRAM)

    def _callback_on_voltage_ratio_change(self, voltageRatio) -> None:
        currentWeight = (voltageRatio - _OFFSET) * _GAIN
        currentForce = currentWeight * _GRAVITY_CONSTANT
        socket.sendto(bytes(str(currentForce), encoding="ascii"), (ip, port))

    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput0.openWaitForAttachment(500)
    voltageRatioInput0.setBridgeGain(4)
    voltageRatioInput0.setDataInterval(1)
    voltageRatioInput0.setOnVoltageRatioChangeHandler(_callback_on_voltage_ratio_change)
    input(">>> Press any key to stop the force measurement..")
    voltageRatioInput0.close()
