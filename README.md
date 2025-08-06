# Modern Shutdown Scheduler

## Overview
Modern Shutdown Scheduler is a sleek and user-friendly PyQt6-based application for scheduling system shutdowns. It features a modern UI with dynamic animations and color transitions based on the time of day.

## Features
- Schedule system shutdowns with a slider-based time picker.
- Dynamic background and slider color transitions.
- Sun and moon animations based on the time of day.
- Cancel scheduled shutdowns with a single click.
- System log for tracking actions.

## Requirements
- **Operating System**: Windows (only)
- **Python Version**: Python 3.9 or higher
- **Dependencies**:
  - PyQt6
  - Other standard Python libraries (e.g., `ctypes`, `subprocess`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/KristupasJon/ModernShutdownScheduler-Win.git
   cd ModernShutdownScheduler-Win
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/ModernShutdownScheduler.py
   ```

## Building the Executable
To package the application into a standalone `.exe` file:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the following command:
   ```bash
   pyinstaller --onefile --noconsole --clean --icon=assets/sun.png --add-data "assets;assets" --name "ModernShutdownScheduler" src/ModernShutdownScheduler.py
   ```

3. The executable will be located in the `dist/` folder.

## Usage
1. Launch the application.
2. Use the slider to set the shutdown time.
3. Click **Schedule Shutdown** to confirm.
4. To cancel, click **Cancel Shutdown**.

## License
This project is licensed under the [MIT License](LICENSE).

## Contributing
Feel free to submit issues or pull requests to improve the project.

