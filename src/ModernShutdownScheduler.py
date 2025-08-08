import sys
import os
import subprocess
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSlider, QProgressBar, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from datetime import datetime, timedelta

if platform.system() != "Windows":
    app = QApplication([])
    QMessageBox.critical(None, "Unsupported OS", "This application can only run on Windows.")
    sys.exit()

MINUTES_IN_DAY = 24 * 60
DEFAULT_SHUTDOWN_OFFSET = 1
SLIDER_TICK_COUNT = 13
ICON_SIZE = 100
WINDOW_OPACITY = 1
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
MORNING_COLOR = (255, 200, 120)
DAY_COLOR = (255, 255, 255)
EVENING_COLOR = (255, 140, 70)
NIGHT_COLOR = (0, 0, 0)
BLUE_COLOR = (79, 140, 255)
ORANGE_COLOR = (220, 140, 60)
RED_COLOR = (255, 60, 60)
COLOR_TRANSITION_MINUTES = 240

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

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
            background: #e6e6e6;
            border-radius: 22px;
            height: 22px;
            text-align: center;
            color: #222;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            border: 2px solid #bdbdbd;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #a084e8);
            border-radius: 22px;
            margin: 0px;
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
        self.time_format_mode = '24'
        self.initUI()

    def get_time_period(self, time_obj=None):
        if time_obj is None:
            time_obj = datetime.now()
        hour = time_obj.hour
        if 5 <= hour < 8:
            return "morning"
        elif 8 <= hour < 19:
            return "day"
        elif 19 <= hour < 22:
            return "evening"
        else:
            return "night"

    def get_smooth_colors(self, time_obj=None):
        if time_obj is None:
            time_obj = datetime.now()
        hour = time_obj.hour
        minute = time_obj.minute
        total_minutes = hour * 60 + minute
        morning_start = 5 * 60
        morning_end = 5 * 60 + COLOR_TRANSITION_MINUTES
        day_start = 8 * 60
        day_end = 8 * 60 + COLOR_TRANSITION_MINUTES
        evening_start = 19 * 60
        evening_end = 19 * 60 + COLOR_TRANSITION_MINUTES
        night_start = 22 * 60
        night_end = 22 * 60 + COLOR_TRANSITION_MINUTES
        if total_minutes < morning_start:
            bg_color = NIGHT_COLOR; text_color = (255, 255, 255)
        elif total_minutes < morning_end:
            progress = (total_minutes - morning_start) / COLOR_TRANSITION_MINUTES
            bg_color = self.interpolate_color(NIGHT_COLOR, MORNING_COLOR, progress)
            text_color = self.interpolate_color((255, 255, 255), (50, 50, 50), progress)
        elif total_minutes < day_start:
            bg_color = MORNING_COLOR; text_color = (50, 50, 50)
        elif total_minutes < day_end:
            progress = (total_minutes - day_start) / COLOR_TRANSITION_MINUTES
            bg_color = self.interpolate_color(MORNING_COLOR, DAY_COLOR, progress); text_color = (50, 50, 50)
        elif total_minutes < evening_start:
            bg_color = DAY_COLOR; text_color = (50, 50, 50)
        elif total_minutes < evening_end:
            progress = (total_minutes - evening_start) / COLOR_TRANSITION_MINUTES
            bg_color = self.interpolate_color(DAY_COLOR, EVENING_COLOR, progress); text_color = self.interpolate_color((50, 50, 50), (255, 255, 255), progress)
        elif total_minutes < night_start:
            bg_color = EVENING_COLOR; text_color = (255, 255, 255)
        elif total_minutes < night_end:
            progress = (total_minutes - night_start) / COLOR_TRANSITION_MINUTES
            bg_color = self.interpolate_color(EVENING_COLOR, NIGHT_COLOR, progress); text_color = (255, 255, 255)
        else:
            bg_color = NIGHT_COLOR; text_color = (255, 255, 255)
        return bg_color, text_color

    def get_smooth_slider_color(self, time_obj=None):
        if time_obj is None:
            time_obj = datetime.now()
        hour = time_obj.hour; minute = time_obj.minute; total_minutes = hour * 60 + minute
        morning_start = 5 * 60; morning_end = 5 * 60 + COLOR_TRANSITION_MINUTES
        day_start = 8 * 60; day_end = 8 * 60 + COLOR_TRANSITION_MINUTES
        evening_start = 19 * 60; evening_end = 19 * 60 + COLOR_TRANSITION_MINUTES
        night_start = 22 * 60; night_end = 22 * 60 + COLOR_TRANSITION_MINUTES
        if total_minutes < morning_start:
            return (100, 100, 200)
        elif total_minutes < morning_end:
            progress = (total_minutes - morning_start) / COLOR_TRANSITION_MINUTES
            return self.interpolate_color((100, 100, 200), ORANGE_COLOR, progress)
        elif total_minutes < day_start:
            return ORANGE_COLOR
        elif total_minutes < day_end:
            progress = (total_minutes - day_start) / COLOR_TRANSITION_MINUTES
            return self.interpolate_color(ORANGE_COLOR, BLUE_COLOR, progress)
        elif total_minutes < evening_start:
            return BLUE_COLOR
        elif total_minutes < evening_end:
            progress = (total_minutes - evening_start) / COLOR_TRANSITION_MINUTES
            return self.interpolate_color(BLUE_COLOR, RED_COLOR, progress)
        elif total_minutes < night_start:
            return RED_COLOR
        elif total_minutes < night_end:
            progress = (total_minutes - night_start) / COLOR_TRANSITION_MINUTES
            return self.interpolate_color(RED_COLOR, (100, 100, 200), progress)
        else:
            return (100, 100, 200)

    def get_icon_for_period(self, period):
        if period == "morning": return self.morning_icon
        if period == "day": return self.day_icon
        if period == "evening": return self.evening_icon
        return self.night_icon

    def create_icon(self, path):
        return QIcon(path)

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

    def update_tick_label_colors(self, color_rgb):
        if not hasattr(self, 'ticks_layout'):
            return
        color_str = self.rgb_to_string(color_rgb)
        for i in range(self.ticks_layout.count()):
            item = self.ticks_layout.itemAt(i)
            if item:
                w = item.widget()
                if isinstance(w, QLabel):
                    w.setStyleSheet(f"color: {color_str}; font-size: 12px;")

    def format_time(self, dt: datetime) -> str:
        if self.time_format_mode == '12':
            return dt.strftime('%I:%M %p').lstrip('0')
        return dt.strftime('%H:%M')

    def on_time_format_changed(self, index):
        chosen = self.time_format_combo.currentData()
        if chosen in ('24', '12'):
            self.time_format_mode = chosen
            self.update_time_label(self.time_input.value())
            self.update_slider_labels()

    def on_opacity_changed(self, value):
        new_opacity = value / 100.0
        self.setWindowOpacity(new_opacity)
        if hasattr(self, 'opacity_value_label'):
            self.opacity_value_label.setText(f"Opacity: {value}%")

    def initUI(self):
        self.setWindowTitle('Modern Shutdown Scheduler')
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowOpacity(WINDOW_OPACITY)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        app_icon_path = resource_path("assets/icons/icon.ico")
        self.setWindowIcon(QIcon(app_icon_path))

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

        
        settings_row = QHBoxLayout()
        settings_row.setContentsMargins(0, 0, 0, 0)

        tf_label = QLabel('Time Format:')
        tf_label.setStyleSheet('font-size: 12px;')
        settings_row.addWidget(tf_label)
        self.time_format_combo = QComboBox()
        self.time_format_combo.addItem('24-hour', userData='24')
        self.time_format_combo.addItem('12-hour (AM/PM)', userData='12')
        self.time_format_combo.currentIndexChanged.connect(self.on_time_format_changed)
        self.time_format_combo.setCurrentIndex(0)
        settings_row.addWidget(self.time_format_combo)

        self.opacity_value_label = QLabel(f'Opacity: {int(WINDOW_OPACITY*100)}%')
        self.opacity_value_label.setStyleSheet('font-size: 12px;')
        settings_row.addWidget(self.opacity_value_label)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(int(WINDOW_OPACITY * 100))
        self.opacity_slider.setFixedWidth(140)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        settings_row.addWidget(self.opacity_slider)
        settings_row.addStretch()
        layout.addLayout(settings_row)

        
        self.app_name_label = QLabel('☀️Modern Shutdown Scheduler🌑')
        self.app_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_name_label.setStyleSheet(Styles.APP_NAME_LABEL)
        layout.addWidget(self.app_name_label, 0)

        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        
        self.morning_icon = self.create_icon(resource_path("assets/images/morning.png"))
        self.day_icon = self.create_icon(resource_path("assets/images/day.png"))
        self.evening_icon = self.create_icon(resource_path("assets/images/evening.png"))
        self.night_icon = self.create_icon(resource_path("assets/images/night.png"))
        current_period = self.get_time_period(datetime.now())
        icon = self.get_icon_for_period(current_period)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setPixmap(icon.pixmap(ICON_SIZE, ICON_SIZE).scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_hbox = QHBoxLayout()
        icon_hbox.addStretch()
        icon_hbox.addWidget(self.icon_label)
        icon_hbox.addStretch()
        layout.addLayout(icon_hbox)

        
        self.time_value_label = QLabel('')
        self.time_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_value_label.setStyleSheet(Styles.TIME_VALUE_LABEL)
        layout.addWidget(self.time_value_label)

        
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

        
        self.dynamic_timer = QTimer(self)
        self.dynamic_timer.timeout.connect(self.check_minute_change)
        self.dynamic_timer.start(1000)
        self.last_minute = datetime.now().minute

    def update_background_color(self):
        now = datetime.now()
        offset_minutes = self.time_input.value() if hasattr(self, 'time_input') else DEFAULT_SHUTDOWN_OFFSET
        target_time = now + timedelta(minutes=offset_minutes)
        
        bg_color, text_color = self.get_smooth_colors(target_time)
        slider_color = self.get_smooth_slider_color(target_time)

        color_style = f"background: {self.rgb_to_string(bg_color)}; border-radius: 32px;"
        text_color_str = self.rgb_to_string(text_color)
        self.centralWidget().setStyleSheet(f"{color_style} color: {text_color_str};")

        if hasattr(self, 'app_name_label'):
            self.app_name_label.setStyleSheet(f'font-size: 24px; font-weight: bold; color: {text_color_str}; margin-bottom: 16px;')
        
        self.update_tick_label_colors(text_color)

        slider_color_str = self.rgb_to_string(slider_color)
        if hasattr(self, 'time_input'):
            self.time_input.setStyleSheet(f"QSlider::handle:horizontal {{ background: {slider_color_str}; border: 2px solid #fff; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }} QSlider::sub-page:horizontal {{ background: {slider_color_str}; border-radius: 6px; }} QSlider::groove:horizontal {{ border: none; height: 12px; background: rgba(255,255,255,0.12); border-radius: 6px; }}")

    def update_sun_moon_animation(self, value):
        try:
            now = datetime.now()
            target_time = now + timedelta(minutes=value)
            target_period = self.get_time_period(target_time)
            icon = self.get_icon_for_period(target_period)
            self.icon_label.setPixmap(icon.pixmap(ICON_SIZE, ICON_SIZE).scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            self.log_message(f"Error in icon animation: {str(e)}")

    def update_time_label(self, value):
        target = self.get_shutdown_time(value)
        text = f"Shutdown at {self.format_time(target)}"
        self.time_value_label.setText(text)
        self.update_background_color()
        _, text_color = self.get_smooth_colors(target)
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
            label_dt = datetime.now() + timedelta(minutes=offset)
            label = QLabel(self.format_time(label_dt))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            label.setStyleSheet("font-size: 12px;")
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
            res = subprocess.run(["shutdown", "/a"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0:
                self.log_message("A shutdown was already pending and has been canceled.")
            now = datetime.now()
            offset_min = self.time_input.value()
            target_time = now + timedelta(minutes=offset_min)
            target_time = target_time.replace(second=0, microsecond=0)
            seconds_until = int((target_time - now).total_seconds())
            self.log_message(
                f"Initiating system shutdown at {self.format_time(target_time)} "
                f"(in {seconds_until} seconds)"
            )
            subprocess.run(["shutdown", "/s", "/t", str(seconds_until)], creationflags=subprocess.CREATE_NO_WINDOW)
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
        self.progress.setStyleSheet("QProgressBar { color: #222; font-weight: bold; font-size: 16px; background: #e6e6e6; border-radius: 22px; border: 2px solid #bdbdbd; text-align: center; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #a084e8); border-radius: 22px; margin: 0px; }")
        self.progress.setFormat(f"{remaining} seconds left")
        if elapsed >= total:
            self.progress_timer.stop()
            self.progress.setStyleSheet(Styles.MAIN_WINDOW)

    def cancel_shutdown(self):
        try:
            subprocess.run(["shutdown", "/a"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
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
