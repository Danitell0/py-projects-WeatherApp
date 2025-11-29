import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie, QFont


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        # ------ UI elements ------
        self.city_label = QLabel("Search City:", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather!", self)

        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)

        self.initUI()
        self.apply_theme(True)

    def apply_theme(self, is_day):
        """Update colors based on day/night"""
        bg_color = "#e8f4ff" if is_day else "#0b132b"
        text_color = "#222" if is_day else "#e0e0e0"

        font_large = QFont()
        font_large.setPointSize(18)
        font_large.setBold(True)
        
        font_medium = QFont()
        font_medium.setPointSize(16)
        
        font_small = QFont()
        font_small.setPointSize(14)

        self.city_label.setFont(font_medium)
        self.temperature_label.setFont(font_large)
        self.description_label.setFont(font_medium)

        for label in [self.city_label, self.temperature_label, self.emoji_label, self.description_label]:
            label.setStyleSheet(f"background: transparent; color: {text_color};")

        self.city_input.setStyleSheet("""
            QLineEdit {
                font-size: 26px;
                padding: 12px;
                border: 2px solid #b0b8c4;
                border-radius: 32px;
                background: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
                background: #ffffff;
            }
        """)

        self.get_weather_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                padding: 12px;
                border-radius: 32px;
                background-color: #A3B18A;
                color: white;
            }
            QPushButton:hover {
                background-color: #588157;
            }
            QPushButton:pressed {
                background-color: #3A5A40;
            }
        """)

        self.setStyleSheet(f"background-color: {bg_color};")

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setFixedSize(450, 600)

        # ------ Main layout ------
        main_layout = QVBoxLayout()
        
        # Add city search elements
        main_layout.addWidget(self.city_label)
        main_layout.addWidget(self.city_input)
        main_layout.addWidget(self.get_weather_button)
        
        main_layout.addSpacing(30)

        main_layout.addWidget(self.temperature_label)
        
        # Add centered GIF using a horizontal layout with stretch
        gif_layout = QHBoxLayout()
        gif_layout.addStretch() 
        gif_layout.addWidget(self.emoji_label)  
        gif_layout.addStretch() 
        main_layout.addLayout(gif_layout)
        
        main_layout.addWidget(self.description_label)
        
        main_layout.addStretch()

        main_layout.setSpacing(10)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        self.setLayout(main_layout)

        for widget in [
            self.city_label, self.city_input,
            self.temperature_label, self.emoji_label,
            self.description_label
        ]:
            widget.setAlignment(Qt.AlignCenter)

        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setFixedSize(200, 200)
        self.emoji_label.setStyleSheet("background: transparent; margin: 0 auto;")
        
        self.temperature_label.setStyleSheet("font-size: 72px; font-weight: bold; background: transparent; text-align: center;")

        self.description_label.setStyleSheet("font-size: 12px; background: transparent; text-align: center;")

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.get_weather_button.clicked.connect(self.get_weather)

    # ---------------- WEATHER LOGIC ----------------

    def get_weather(self):
        api_key = #Please use your own API KEY
        city = self.city_input.text().strip()
        if not city:
            self.display_error("Please enter a city")
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if int(data.get("cod", 0)) == 200:
                self.display_weather(data)
            else:
                self.display_error(data.get("message", "Unknown Error"))

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error:\nCheck your internet")
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error")
        except requests.exceptions.RequestException as e:
            self.display_error(f"Error: {e}")

    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 20px; color: #d9534f; background: transparent; text-align: center;")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 48px; font-weight: bold; background: transparent; text-align: center;")

        temp_c = data["main"]["temp"]
        weather_id = data["weather"][0]["id"]
        description = data["weather"][0]["description"]

        # Day / Night
        sunrise = data["sys"]["sunrise"]
        sunset = data["sys"]["sunset"]
        current_time = data["dt"]
        is_day = sunrise < current_time < sunset
        self.apply_theme(is_day)

        self.temperature_label.setText(f"{temp_c:.0f}°C")
        self.description_label.setText(description.title())

        # ------ Animated Emoji ------
        gif_path = self.get_weather_gif(weather_id)
        if gif_path:
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(80, 80))
            self.emoji_label.setMovie(movie)
            self.emoji_label.setScaledContents(True)
            movie.start()
        else:
            self.emoji_label.clear()

    # ------ GIF MAPPINGS ------

    def get_weather_gif(self, weather_id):
        if 200 <= weather_id <= 232: return "backgrounds/storm.gif"
        if 300 <= weather_id <= 321: return "backgrounds/rain.gif"
        if 500 <= weather_id <= 531: return "backgrounds/rain.gif"
        if 600 <= weather_id <= 622: return "backgrounds/snow.gif"
        if 701 <= weather_id <= 741: return "backgrounds/fog.gif"
        if weather_id == 762: return "backgrounds/volcano.gif"
        if weather_id == 771: return "backgrounds/wind.gif"
        if weather_id == 781: return "backgrounds/tornado.gif"
        if weather_id == 800: return "backgrounds/day_clear.gif"
        if 801 <= weather_id <= 804: return "backgrounds/clouds.gif"
        return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
