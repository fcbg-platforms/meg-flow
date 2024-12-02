[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/gh/fcbg-platforms/meg-flow/graph/badge.svg?token=e6jhOYlSZg)](https://codecov.io/gh/fcbg-platforms/meg-flow)
[![tests](https://github.com/fcbg-platforms/meg-flow/actions/workflows/pytest.yaml/badge.svg?branch=main)](https://github.com/fcbg-platforms/meg-flow/actions/workflows/pytest.yaml)

# MEG-flow

**Title**: Tracking the neural dynamics underlying variations in flow/attentional states
at the timescale of second

The project is composed of a python package `flow` and of a Unity task. The python
package can be installed on all platforms and uses [psychopy](https://www.psychopy.org/)
to control an oddball auditory paradigm.

## Install

On macOS or Windows, the python package can be installed in a virtual environment with
`pip` or [uv](https://docs.astral.sh/uv/) (drop-in replacement for `pip`, recommended):

```bash
$ uv pip install git+https://github.com/fcbg-platforms/meg-flow
```

On Linux, [psychopy](https://www.psychopy.org/) requires the following manual step prior
to the installation of the `flow` package:

- `wxPython` which can be retrieved
  [here](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/) for your platform, or
  compiled locally.
- the system dependencies:

  ```bash
  $ sudo apt install libusb-1.0-0-dev portaudio19-dev libasound2-dev libsdl2-2.0-0
  ```

- the following `ulimits`:

  ```bash
  $ sudo groupadd --force psychopy
  $ sudo usermod -aG psychopy $USER
  $ sudo nano /etc/security/limits.d/99-psychopylimits.conf
  ```

  Set the content of `99-psychopylimits.conf` to:

  ```
  @psychopy   -  nice       -20
  @psychopy   -  rtprio     50
  @psychopy   -  memlock    unlimited
  ```

> [!IMPORTANT]
> As of writing, [psychopy](https://www.psychopy.org/) is still limited to Python 3.10,
> thus make sure to create a virtual environment with a compatible version of Python.

## Usage

The `flow` package has 2 command-line entry-points:

* `forward-force`: to stream the sensor force to Unity.

```bash
$ flow forward-force --help
```

* `oddball`: to start the oddball paradigm.

```bash
$ flow oddball --help
```

The oddball paradigm can be halted and resumed via [ZMQ](https://zeromq.org/) messages.
An example is provided in `script/zmq-control.py`.
