# Installation
## AutoDRIVE Simulator
### MacOS

The macOS installation guide is a bit lengthy, so please refer to [the macOS installation guide](macos.md).

## Windows

First, download the [AutoDRIVE Simulator](https://github.com/Tinker-Twins/AutoDRIVE/releases/download/Simulator-0.3.0/AutoDRIVE_Simulator_Windows.zip).

Then, double-click on the executable file. Should be open :D

## Linux

First, download [AutoDRIVE Simulator](https://github.com/Tinker-Twins/AutoDRIVE/releases/download/Simulator-0.3.0/AutoDRIVE_Simulator_Linux.zip).

Then, double-click on the executable file. Should be open :D

## Connecting to the simulator

### Installing uv

First, install uv, the Python package manager used by the UCI team.

#### Macos and Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | less
```

#### Windows

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | more"
```

### Running example_f1tenth.py

UV will automatically download the correct Python version and the required packages in a virtual environment managed by UV. Therefore, please refrain from using pip or venv on top of UV. Now you are ready to run example_f1tenth.py!

```bash
uv run example_f1tenth.py
```

### Connecting to AutoDRIVE

While `example_f1tenth.py` is running, open the AutoDRIVE application. Then click on "Manual" to switch it to Autonomous mode, and then click on "Disconnected" to connect. Your car should now be driving forward automatically!