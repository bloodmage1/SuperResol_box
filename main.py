import sys
from PySide6.QtWidgets import QApplication
from ui.main_screen import ImproveResolution

if __name__ == '__main__':
    app = QApplication(sys.argv)
    execute_instance = ImproveResolution(app)
    app.exec()