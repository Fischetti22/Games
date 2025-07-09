import sys
import requests
import random
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont
from wallpapers import set_wallpaper_for_condition

# Get API key from environment variable
API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY = "Camden, South Carolina"

if not API_KEY:
    print("Error: OPENWEATHER_API_KEY environment variable not set")
    sys.exit(1)

class WeatherHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.old_pos = self.pos()
        self.refresh_weather()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 180); border-radius: 10px;")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.weather_label = QLabel("Weather: loading...")
        self.temp_label = QLabel("Temp: -- °C")
        self.close_button = QPushButton("X")

        font = QFont("Arial", 12)
        self.weather_label.setFont(font)
        self.temp_label.setFont(font)
        self.weather_label.setStyleSheet("color: white;")
        self.temp_label.setStyleSheet("color: white;")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: red; color: white; border: none;")
        self.close_button.clicked.connect(self.close)

        self.layout.addWidget(self.weather_label)
        self.layout.addWidget(self.temp_label)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.resize(200, 120)
        self.move(100, 100)

        # Refresh every 10 minutes
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_weather)
        self.timer.start(600000)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def refresh_weather(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()

            condition = data['weather'][0]['main']
            temp = data['main']['temp']

            self.weather_label.setText(f"Weather: {condition}")
            self.temp_label.setText(f"Temp: {temp:.1f} °C")

            # Call wallpaper changer here
            set_wallpaper_for_condition(condition)

        except Exception as e:
            self.weather_label.setText("Error fetching weather")
            self.temp_label.setText(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = WeatherHUD()
    hud.show()
    sys.exit(app.exec_())

