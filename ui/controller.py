from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox
from utils.model import SuperresolutionModel

button_size_x = 180
button_size_y = 40
hover_style = """
    QPushButton:hover {
        color: #FFFFFF;
        font-weight: bold;}
"""

class Controller(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.UI초기화()

    def UI초기화(self):
        load_image_widget = QWidget(self)

        self.load_button = QPushButton('Load File', self)
        self.load_button.setFixedSize(button_size_x, button_size_y) 
        self.load_button.setStyleSheet(hover_style)
        self.load_button.clicked.connect(self.load_video)

        self.predict_button = QPushButton('Predict', self)
        self.predict_button.setFixedSize(button_size_x, button_size_y) 
        self.predict_button.setStyleSheet(hover_style)
        self.predict_button.clicked.connect(self.predict_image)

        self.delete_button = QPushButton('Delete', self)
        self.delete_button.setFixedSize(button_size_x, button_size_y) 
        self.delete_button.setStyleSheet(hover_style)
        self.delete_button.clicked.connect(self.delete_image)

        self.progress_bar_label = QLabel('진행상황', self) 
        self.parent.progress_bar = QProgressBar(self)
        # self.progress_bar = QProgressBar(self) 

        agv_state_layout = QVBoxLayout(load_image_widget)
        agv_state_layout.addWidget(self.load_button)
        agv_state_layout.addWidget(self.predict_button)
        agv_state_layout.addWidget(self.delete_button)
        agv_state_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)) 
        agv_state_layout.addWidget(self.progress_bar_label)  
        # agv_state_layout.addWidget(self.progress_bar)
        agv_state_layout.addWidget(self.parent.progress_bar)
        agv_state_layout.addStretch(1)

        load_image_widget.setLayout(agv_state_layout)
        self.setLayout(agv_state_layout)
    
    def load_video(self):
        self.parent.video_path, _ = QFileDialog.getOpenFileName(self, 'Open file', 
                                                         './', "Video Files (*.mp4 *.avi *.mov)")
        if self.parent.video_path:
            QMessageBox.information(self, "알림", f"비디오 경로가 갱신되었습니다: {self.parent.video_path}")
        else:
            QMessageBox.warning(self, "알림", "비디오 파일을 선택하지 않았습니다.")

    def predict_image(self):
        if self.parent.video_path:
            detector = SuperresolutionModel()
            detector.detect_objects_in_video_and_save_frames(self.parent.video_path, 
                                                             self.parent.update_progress)
            QMessageBox.warning(self, "알림", "예측이 완료되었습니다.")
        else:
            QMessageBox.warning(self, "알림", "비디오 파일이 로드되지 않았습니다.")

    def delete_image(self):
        self.parent.label.clear()
        self.parent.label_p.clear()
        self.progress_bar.reset()