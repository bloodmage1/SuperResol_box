from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
import cv2

class OriginalVideo(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.init_ui()

    def UI초기화(self):
        main_screen_layout = QVBoxLayout(self)

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 256, 256) 
        main_screen_layout.addWidget(self.label)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_video)
        main_screen_layout.addWidget(self.play_button)

        self.setLayout(main_screen_layout)
    
    def play_video(self):
        if self.cap:
            self.cap.release()
        if self.parent.video_path:
            self.cap = cv2.VideoCapture(self.parent.video_path)
            self.timer.start(30)
        else:
            QMessageBox.warning(self, "알림", "비디오 파일이 로드되지 않았습니다.")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (256, 256)) 
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(image))
        else:
            self.timer.stop()
            self.cap.release()