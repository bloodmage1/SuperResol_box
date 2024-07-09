from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QScrollArea, QWidget
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet
from ui.original_video import OriginalVideo
from ui.predict_video import PredictVideo
from ui.controller import Controller

class ImproveResolution(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.video_path = None  
        self.cap = None
        self.cap_p = None
        self.progress_bar = None
        self.UI초기화()

    def update_progress(self, frame_count, total_frames):
        self.progress_bar.setValue(frame_count)
        self.progress_bar.setMaximum(total_frames) 

    def UI초기화(self):
        main_box = QHBoxLayout()

        main_box.addStretch(1)
        main_box.addWidget(OriginalVideo(self), 7)
        main_box.addWidget(PredictVideo(self), 7)
        main_box.addWidget(Controller(self), 1)

        self.scroll_area = QScrollArea()
        self.setCentralWidget(self.scroll_area)

        central_widget = QWidget()
        central_widget.setLayout(main_box)
        self.scroll_area.setWidget(central_widget)
        self.scroll_area.setWidgetResizable(True) 

        apply_stylesheet(self.app, theme='light_cyan.xml')
        self.setWindowTitle('초해상도 기기')
        self.setWindowIcon(QIcon('./app_img/Title.png'))
        self.setGeometry(0, 0, 768, 320)
        self.show()

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.cap_p:
            self.cap_p.release()