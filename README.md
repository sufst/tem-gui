<h1 align="center"> TEM GUI </h2>
A cross-platform graphical user interface to read thermistors' temperatures from the BMS CAN.

# Documentation
<h3>Application Modes</h3>

- Reading data from a CAN (needs to be connected to the accum)
- Generating random data (for testing purposes)
<br>

To toggle between different modes use **RANDOM_DATA_DEFINITION** flag in main.py

<h3>Logging Mode</h3>

- DataLogger class used to read modules & thermistors data over certain period of time. You can specify specific format of saving data on your local machine(default is csv). All logged information is saved upon closing the app in **_logs_** folder
<br>

To toggle datalogger mode ON/OFF use **ENABLE_LOGGING** flag in main.py

<br>

More on **SUFST Documentation** ___02-accumulator/chapter/thermistors-gui___ page.

# Setup
1. **Clone the repository:**</br>
Use SSH code if you want to contribute

  ```bash
  git clone https://github.com/sufst/tem-gui.git
  cd tem-gui
  ```

2. **Run virtual environment**
  ```bash
  python -m venv venv
  venv/Scripts/activate
  ```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run:**
```bash
cd source
python main.py
```

# Contributing

Before contributing to this project, make sure to familiarise yourself with the
[project-specific contributing guidelines](https://github.com/sufst/vcu/blob/main/.github/CONTRIBUTING_EXTRA.md).

# Dependencies
- **Python**
- **<a href="https://kivy.org/">Kivy</a>** - cross platform for GUI apps Development

# Related Projects
- **<a href="https://github.com/sufst/tem-firmware">tem-firmware</a>** - BMS Firmware


