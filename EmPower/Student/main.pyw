import os
import sys
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication
from Frontend.src.Home import Home
from Frontend.src.SplashScreen import SplashScreen
from Frontend.Student_UI.ui_student_info import Ui_Student_Info
from Frontend.src.Add_Student_Info import Add_Student_info

app = QApplication(sys.argv)
splash = SplashScreen()

# Center the splash screen window on the screen
splash_width = splash.width()
splash_height = splash.height()

screen = app.primaryScreen()

if screen is not None:
    screen_geometry = screen.availableGeometry()
else:
    # Fallback if no screen was found (e.g., headless environment)
    # Adjust fallback size as appropriate for your app
    screen_geometry = QRect(0, 0, 1024, 768)

x = (screen_geometry.width() - splash_width) // 2
y = (screen_geometry.height() - splash_height) // 2
splash.move(x, y)

# show the splash window
splash.show()
splash.progress()

# MAIN WINDOW
window = Home()
window.showMaximized()
window.show()

splash.finish(window)

sys.exit(app.exec_())
