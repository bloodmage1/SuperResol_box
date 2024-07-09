from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
import cv2

class PredictVideo(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.cap_p = None
        self.timer_p = QTimer()
        self.timer_p.timeout.connect(self.update_frame_p)
        self.UI초기화()

    def UI초기화(self):
        main_screen_layout = QVBoxLayout(self)

        self.label_p = QLabel(self)
        self.label_p.setGeometry(10, 10, 256, 256)  
        main_screen_layout.addWidget(self.label_p)

        self.play_button_p = QPushButton('Play', self)
        self.play_button_p.clicked.connect(self.play_video_p)
        main_screen_layout.addWidget(self.play_button_p)

        self.setLayout(main_screen_layout)

    def play_video_p(self):
        if self.cap_p:
            self.cap_p.release()
        self.cap_p = cv2.VideoCapture("Resolution_improved_vid.mp4")
        self.timer_p.start(30)

    def update_frame_p(self):
        ret, frame = self.cap_p.read()
        if ret:
            frame = cv2.resize(frame, (256, 256)) 
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
            self.label_p.setPixmap(QPixmap.fromImage(image))
        else:
            self.timer_p.stop()
            self.cap_p.release()