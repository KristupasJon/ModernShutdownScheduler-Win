import sys
import os
import subprocess
import ctypes
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSlider, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon
from datetime import datetime, timedelta

TOTAL_SECONDS_IN_DAY = 24 * 60 * 60
MINUTES_IN_DAY = 24 * 60
DEFAULT_SHUTDOWN_OFFSET = 1
SLIDER_TICK_COUNT = 20
ICON_SIZE = 128

DAY_COLOR = (255, 255, 255)
MID_COLOR = (220, 140, 60)
NIGHT_COLOR = (0, 0, 0)
BLUE_COLOR = (79, 140, 255)
ORANGE_COLOR = (220, 140, 60)
RED_COLOR = (255, 60, 60)

if platform.system() != "Windows":
    app = QApplication([])
    QMessageBox.critical(None, "Unsupported OS", "This application can only run on Windows.")
    sys.exit()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        f'"{os.path.abspath(__file__)}"', None, 1
    )
    sys.exit()

class Styles:
    MAIN_WINDOW = """
        QMainWindow {
            background: transparent;
        }
        QWidget {
            font-family: 'Segoe UI', 'San Francisco', 'Arial', sans-serif;
            color: #fff;
        }
        QLabel {
            color: #fff;
            font-size: 16px;
            font-weight: 500;
            border-radius: 32px;
        }
        QTextEdit {
            background: rgba(40, 40, 50, 0.7);
            color: #fff;
            border: 1.5px solid #3d3d3d;
            border-radius: 18px;
            padding: 10px;
            font-size: 14px;
            max-height: 120px;
        }
        QSlider::groove:horizontal {
            border: none;
            height: 12px;
            background: rgba(255,255,255,0.12);
            border-radius: 6px;
        }
        QSlider::handle:horizontal {
            background: #4f8cff;
            border: 2px solid #fff;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        QSlider::handle:horizontal:hover {
            background: #3a6eea;
        }
        QSlider::sub-page:horizontal {
            background: #4f8cff;
            border-radius: 6px;
        }
        QProgressBar {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            height: 18px;
            text-align: center;
            color: #fff;
            font-size: 14px;
            margin-bottom: 10px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #1e2a4a);
            border-radius: 12px;
        }
    """

    CENTRAL_WIDGET = """
        background: rgba(30, 30, 40, 0.7);
        border-radius: 32px;
    """

    APP_NAME_LABEL = "font-size: 24px; font-weight: bold; color: #fff; margin-bottom: 16px;"

    TIME_VALUE_LABEL = "font-size: 18px; font-weight: 600; color: #fff; margin-bottom: 8px;"

    SLIDER_TICK_LABEL = "color: #bbb; font-size: 12px;"

    SHUTDOWN_BUTTON = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c7a4ff, stop:1 #a084e8);
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid #b39ddb;
            border-radius: 10px;
            padding: 10px 20px;
            margin-bottom: 8px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b39ddb, stop:1 #c7a4ff);
        }
    """
    CANCEL_BUTTON = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0bbff, stop:1 #b39ddb);
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid #a084e8;
            border-radius: 10px;
            padding: 10px 20px;
            margin-bottom: 8px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b39ddb, stop:1 #e0bbff);
        }
    """

class ShutdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def create_icon(self, path):
        return QIcon(path)
    
    def calculate_transition_factor(self, offset_minutes=None):
        now = datetime.now()
        if offset_minutes is None:
            offset_minutes = self.time_input.value()
        shutdown_time = now + timedelta(minutes=offset_minutes)
        time_diff = (shutdown_time - now).total_seconds()
        return min(1.0, max(0.0, time_diff / TOTAL_SECONDS_IN_DAY))
    
    def interpolate_color(self, color1, color2, factor):
        r = int(color1[0] * (1 - factor) + color2[0] * factor)
        g = int(color1[1] * (1 - factor) + color2[1] * factor)
        b = int(color1[2] * (1 - factor) + color2[2] * factor)
        return r, g, b
    
    def rgb_to_string(self, rgb_tuple):
        return f"rgb({rgb_tuple[0]}, {rgb_tuple[1]}, {rgb_tuple[2]})"
    
    def get_shutdown_time(self, offset_minutes=None):
        if offset_minutes is None:
            offset_minutes = self.time_input.value()
        return datetime.now() + timedelta(minutes=offset_minutes)
    
    def update_label_text_color(self, label, color_rgb):
        current_style = label.styleSheet()
        style_parts = []
        for part in current_style.split(';'):
            if part.strip() and not part.strip().startswith('color:'):
                style_parts.append(part.strip())
        style_parts.append(f'color: {self.rgb_to_string(color_rgb)}')
        label.setStyleSheet('; '.join(style_parts) + ';')

    def initUI(self):
        self.setWindowTitle('Modern Shutdown Scheduler')
        self.setFixedSize(700, 700)
        self.setWindowOpacity(0.98)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet(Styles.MAIN_WINDOW)

        central_widget = QWidget()
        central_widget.setStyleSheet(Styles.CENTRAL_WIDGET)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(18)
        layout.setContentsMargins(30, 30, 30, 30)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 0)
        title_bar.addStretch()
        self.close_button = QPushButton('❌')
        self.close_button.clicked.connect(self.close)
        title_bar.addWidget(self.close_button)
        layout.addLayout(title_bar)

        self.app_name_label = QLabel('☀️Modern Shutdown Scheduler🌑')
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_name_label.setStyleSheet(Styles.APP_NAME_LABEL)
        layout.addWidget(self.app_name_label, 0)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.moon_icon = self.create_icon(os.path.join(dir_path, "..", "assets", "moon.png"))
        self.sun_icon = self.create_icon(os.path.join(dir_path, "..", "assets", "sun.png"))
        now = datetime.now()
        is_day = 6 <= now.hour < 18
        icon = self.sun_icon if is_day else self.moon_icon

        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon.pixmap(ICON_SIZE, ICON_SIZE))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)
        slider_layout.setContentsMargins(0, 0, 0, 0)

        slider_label = QLabel('Pick shutdown time:')
        slider_layout.addWidget(slider_label)

        self.time_input = QSlider(Qt.Orientation.Horizontal)
        self.time_input.setRange(1, MINUTES_IN_DAY)
        self.time_input.setValue(DEFAULT_SHUTDOWN_OFFSET)
        self.time_input.setTickInterval(60)
        self.time_input.setSingleStep(1)
        self.time_input.setPageStep(60)
        self.time_input.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.time_input.valueChanged.connect(self.update_time_label)
        slider_layout.addWidget(self.time_input)

        self.slider_ticks = QWidget()
        self.ticks_layout = QHBoxLayout(self.slider_ticks)
        self.ticks_layout.setContentsMargins(0, 0, 0, 0)
        self.ticks_layout.setSpacing(0)
        self.update_slider_labels()
        slider_layout.addWidget(self.slider_ticks)
        layout.addWidget(slider_container)

        self.time_value_label = QLabel('')
        self.time_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_value_label.setStyleSheet(Styles.TIME_VALUE_LABEL)
        layout.addWidget(self.time_value_label)
        self.update_time_label(self.time_input.value())

        self.shutdown_button = QPushButton('Schedule Shutdown')
        self.shutdown_button.clicked.connect(self.initiate_shutdown)
        self.shutdown_button.setStyleSheet(Styles.SHUTDOWN_BUTTON)
        layout.addWidget(self.shutdown_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.cancel_button = QPushButton('Cancel Shutdown')
        self.cancel_button.clicked.connect(self.cancel_shutdown)
        self.cancel_button.setStyleSheet(Styles.CANCEL_BUTTON)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        console_label = QLabel('System Log:')
        layout.addWidget(console_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(120)
        layout.addWidget(self.console)

        self.offset = None
        central_widget.mousePressEvent = self.mousePressEvent
        central_widget.mouseMoveEvent = self.mouseMoveEvent

        self.sun_animation = QPropertyAnimation(self.icon_label, b"geometry")
        self.moon_animation = QPropertyAnimation(self.icon_label, b"geometry")

        self.sun_start_rect = QRect(100, 100, ICON_SIZE, ICON_SIZE)
        self.sun_end_rect = QRect(500, 100, ICON_SIZE, ICON_SIZE)
        self.moon_start_rect = QRect(500, 100, ICON_SIZE, ICON_SIZE)
        self.moon_end_rect = QRect(100, 100, ICON_SIZE, ICON_SIZE)

        self.sun_animation.setDuration(1000)
        self.sun_animation.setStartValue(self.sun_start_rect)
        self.sun_animation.setEndValue(self.sun_end_rect)

        self.moon_animation.setDuration(1000)
        self.moon_animation.setStartValue(self.moon_start_rect)
        self.moon_animation.setEndValue(self.moon_end_rect)

        self.dynamic_timer = QTimer(self)
        self.dynamic_timer.timeout.connect(self.check_minute_change)
        self.dynamic_timer.start(1000)
        self.last_minute = datetime.now().minute

    def update_background_color(self):
        transition_factor = self.calculate_transition_factor()

        if transition_factor < 0.25:
            local_factor = transition_factor / 0.25
            bg_color = self.interpolate_color(DAY_COLOR, MID_COLOR, local_factor)
            text_color = self.interpolate_color(NIGHT_COLOR, DAY_COLOR, transition_factor)
        else:
            local_factor = (transition_factor - 0.25) / 0.75
            bg_color = self.interpolate_color(MID_COLOR, NIGHT_COLOR, local_factor)
            text_color = self.interpolate_color(NIGHT_COLOR, DAY_COLOR, transition_factor)

        color_style = f"background: {self.rgb_to_string(bg_color)}; border-radius: 32px;"
        text_color_str = self.rgb_to_string(text_color)
        self.centralWidget().setStyleSheet(f"{color_style} color: {text_color_str};")

        if hasattr(self, 'app_name_label'):
            self.app_name_label.setStyleSheet(f'font-size: 24px; font-weight: bold; color: {text_color_str}; margin-bottom: 16px;')

        if transition_factor < 0.25:
            slider_local = transition_factor / 0.25
            slider_color = self.interpolate_color(BLUE_COLOR, ORANGE_COLOR, slider_local)
        else:
            slider_local = (transition_factor - 0.25) / 0.75
            slider_color = self.interpolate_color(ORANGE_COLOR, RED_COLOR, slider_local)
        slider_color_str = self.rgb_to_string(slider_color)
        self.time_input.setStyleSheet(f"QSlider::handle:horizontal {{ background: {slider_color_str}; border: 2px solid #fff; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }} QSlider::sub-page:horizontal {{ background: {slider_color_str}; border-radius: 6px; }} QSlider::groove:horizontal {{ border: none; height: 12px; background: rgba(255,255,255,0.12); border-radius: 6px; }}")

    def update_sun_moon_animation(self, value):
        try:
            transition_factor = value / MINUTES_IN_DAY
            sun_x = int(self.sun_start_rect.x() * (1 - transition_factor) + self.sun_end_rect.x() * transition_factor)
            moon_x = int(self.moon_start_rect.x() * transition_factor + self.moon_end_rect.x() * (1 - transition_factor))
            self.icon_label.setGeometry(sun_x, self.sun_start_rect.y(), ICON_SIZE, ICON_SIZE)
            sun_opacity = 1 - transition_factor
            moon_opacity = transition_factor
            if sun_opacity > moon_opacity:
                self.icon_label.setPixmap(self.sun_icon.pixmap(ICON_SIZE, ICON_SIZE))
            else:
                self.icon_label.setPixmap(self.moon_icon.pixmap(ICON_SIZE, ICON_SIZE))
        except Exception as e:
            self.log_message(f"Error in sun/moon animation: {str(e)}")

    def update_time_label(self, value):
        target = self.get_shutdown_time(value)
        text = f"Shutdown at {target.hour:02d}:{target.minute:02d}"
        self.time_value_label.setText(text)
        self.update_background_color()
        transition_factor = self.calculate_transition_factor(value)
        text_color = self.interpolate_color(NIGHT_COLOR, DAY_COLOR, transition_factor)
        text_color_str = f'font-size: 18px; font-weight: 600; color: {self.rgb_to_string(text_color)}; margin-bottom: 8px;'
        self.time_value_label.setStyleSheet(text_color_str)
        self.update_sun_moon_animation(value)

    def update_slider_labels(self):
        while self.ticks_layout.count():
            item = self.ticks_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()
        for i in range(SLIDER_TICK_COUNT):
            offset = int(i * MINUTES_IN_DAY / (SLIDER_TICK_COUNT - 1))
            label_time = (datetime.now() + timedelta(minutes=offset)).time()
            label = QLabel(label_time.strftime("%H:%M"))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(Styles.SLIDER_TICK_LABEL)
            self.ticks_layout.addWidget(label, 1)
        self.update_background_color()

    def check_minute_change(self):
        current_minute = datetime.now().minute
        if current_minute != self.last_minute:
            self.update_time_label(self.time_input.value())
            self.update_slider_labels()
            self.last_minute = current_minute

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)
            event.accept()

    def initiate_shutdown(self):
        try:
            res = subprocess.run(["shutdown", "/a"], capture_output=True)
            if res.returncode == 0:
                self.log_message("A shutdown was already pending and has been canceled.")
            now = datetime.now()
            offset_min = self.time_input.value()
            target_time = now + timedelta(minutes=offset_min)
            target_time = target_time.replace(second=0, microsecond=0)
            seconds_until = int((target_time - now).total_seconds())
            self.log_message(
                f"Initiating system shutdown at {target_time.hour:02d}:{target_time.minute:02d} "
                f"(in {seconds_until} seconds)"
            )
            subprocess.run(["shutdown", "/s", "/t", str(seconds_until)])
            self.progress.setVisible(True)
            self.progress.setMaximum(seconds_until)
            self.progress.setValue(0)
            self.progress_timer = QTimer()
            self.progress_timer.timeout.connect(self.update_progress)
            self.progress_timer.start(1000)
            self.progress_start_time = now
            self.progress_end_time = target_time
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred: {str(e)}"
            )

    def hide_progress_bar(self):
        self.progress.setVisible(False)
        if hasattr(self, 'progress_timer'):
            self.progress_timer.stop()

    def update_progress(self):
        now = datetime.now()
        total = int((self.progress_end_time - self.progress_start_time).total_seconds())
        elapsed = int((now - self.progress_start_time).total_seconds())
        remaining = max(0, total - elapsed)
        self.progress.setValue(elapsed)
        self.progress.setFormat(f"{remaining} seconds left")
        if elapsed >= total:
            self.progress_timer.stop()

    def cancel_shutdown(self):
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            self.log_message("Shutdown has been canceled.")
            self.hide_progress_bar()
            self.update_slider_labels()
        except subprocess.CalledProcessError:
            self.log_message("Failed to cancel shutdown - No shutdown was scheduled.")
            QMessageBox.warning(
                self,
                "Warning",
                "No shutdown was scheduled to cancel."
            )
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
    def log_message(self, message):
        if hasattr(self, 'console'):
            self.console.append(f"> {message}")

def main():
    app = QApplication([])
    app.setStyle('Fusion')
    window = ShutdownApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
