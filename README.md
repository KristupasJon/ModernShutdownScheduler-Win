# Modern Shutdown Scheduler

## Overview
Modern Shutdown Scheduler is a sleek, super lightweight, and user-friendly PyQt6-based application for scheduling system shutdowns. It features a modern UI with dynamic animations and color transitions based on the time of day, and uses very little memory.

<table>
  <tr>
    <td>
      <img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/32b3ba41-703f-4762-b0a1-a9cafedf8760" />
    </td>
    <td>
      <img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/bd00dc28-7f3d-4f17-85e3-c05ac65203dd" />
    </td>
  </tr>
  <tr>
    <td>
      <img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/91922f32-f1a1-4168-bc0f-44007f175160" />
    </td>
    <td>
      <img width="700" height="700" alt="image" src="https://github.com/user-attachments/assets/ce74ef2c-ca92-4c38-baa6-e8364cc6d3dc" />
    </td>
  </tr>
</table>



## Features
- Super lightweight and uses very little memory
- Schedule system shutdowns with a slider-based time picker
- Dynamic background and slider color transitions
- Sun and moon animations based on the time of day
- Cancel scheduled shutdowns with a single click
- System log for tracking actions

## Requirements
- **Operating System**: Windows

## Download or Clone

You can download the latest release directly from the [Releases](https://github.com/KristupasJon/ModernShutdownScheduler-Win/releases/tag/stable) page.

Alternatively, you may choose to clone the repository and run the application as described in the [Installation](#installation) section.

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

Requirements:
- **Operating System**: Windows (only)
- **Python Version**: Python 3.9 or higher
- **Dependencies**:
  - PyQt6
  - Other standard Python libraries (e.g., `ctypes`, `subprocess`)

To package the application into a standalone `.exe` file:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the following command:
   ```bash
   pyinstaller --onefile --noconsole --clean --icon=assets/icons/icon.ico --add-data "assets;assets" --name "ModernShutdownScheduler" src/ModernShutdownScheduler.py
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

