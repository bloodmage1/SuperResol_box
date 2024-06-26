import sys
sys.coinit_flags = 2

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

from qt_material import apply_stylesheet
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from time import time, sleep
import os
import cv2
import numpy as np
import warnings

import torch

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

button_size_x = 180
button_size_y = 40
edit_line_size = 120
c_size = 30

hover_style = """
    QPushButton:hover {
        color: #FFFFFF;
        font-weight: bold;}
"""

import segmentation_models_pytorch as smp

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

class Superresolution_model:
    def __init__(self):
        self.model = smp.UnetPlusPlus(encoder_name="efficientnet-b7", 
                                encoder_weights=None, 
                                in_channels=3, 
                                classes=3).to(device)

        self.model.load_state_dict(torch.load("./best_model_b7_3.pth"))
        self.model.eval()

    def detect_objects_in_video_and_save_frames(self, video_path, progress_callback, output_dir="./testtest", frame_rate=10):
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        patch_size = 96
        stride = int(patch_size / 2)
        batch_size = 1
        frame_count = 0

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total = np.zeros(shape=(total_frames, 256, 256, 3))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (256, 256))
            img = frame / 255
        
            crop = []
            position = []
            batch_count = 0
            

            result_img = np.zeros(shape=(img.shape[0], img.shape[1], 3))
            voting_mask = np.zeros(shape=(img.shape[0], img.shape[1], 3))

            for top in range(0, img.shape[0], stride):
                for left in range(0, img.shape[1], stride):
                    piece = np.ones([patch_size, patch_size, 3], np.float32)
                    temp = img[top: top + patch_size, left: left + patch_size, :]
                    piece[:temp.shape[0], :temp.shape[1], :] = temp
                    crop.append(piece)
                    position.append([top, left])
                    batch_count += 1
                    if batch_count == batch_size:
                        input_ = np.array(crop)
                        input_ = torch.from_numpy(input_.transpose(0, 3, 1, 2)).to(device)

                        with torch.no_grad():
                            pred = self.model(input_)

                        pred = (pred + input_)
                        pred = pred.cpu().detach().numpy().transpose(0, 2, 3, 1).astype('float')

                        for num, (top, left) in enumerate(position):
                            piece = pred[num]
                            piece = np.clip(piece, 0, 1)

                            h, w, c = result_img[top:top + patch_size, left:left + patch_size].shape
                            result_img[top:top + patch_size, left:left + patch_size] += piece[:h, :w]
                            voting_mask[top:top + patch_size, left:left + patch_size] += 1

                        batch_count = 0
                        crop = []
                        position = []
            
            voting_mask[voting_mask == 0] = 1
            image_file = result_img / voting_mask
            total[frame_count, :, :, :] = image_file  
                
            frame_filename = os.path.join(output_dir, f'frame_{frame_count}.png')
            # rgb_image = cv2.cvtColor((total[frame_count] * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
            rgb_image = (total[frame_count] * 255).astype(np.uint8)
            cv2.imwrite(frame_filename, rgb_image)
            frame_count += 1

            progress_callback(frame_count, total_frames)
            
        cap.release()
        images = [img for img in os.listdir(output_dir) if img.endswith(".png")]
        images.sort() 

        first_frame_path = os.path.join(output_dir, images[0])
        frame = cv2.imread(first_frame_path)
        height, width, layers = frame.shape

        frame = cv2.imread(first_frame_path)
        height, width, layers = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        video_writer = cv2.VideoWriter("Resolution_improved_vid.mp4", fourcc, frame_rate, (width, height))
        for image in images:
            img_path = os.path.join(output_dir, image)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()

class Improve_resolution(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.video_path = None  # video_path 초기화
        self.cap = None
        self.cap_p = None

        self.UI초기화()

    def update_progress(self, frame_count, total_frames):
        self.progress_bar.setValue(frame_count)
        self.progress_bar.setMaximum(total_frames) 

    def UI초기화(self):
        Main_box = QHBoxLayout()

        Main_box.addStretch(1)
        Main_box.addWidget(self.Original_Video(), 7)
        Main_box.addWidget(self.Predict_Video(), 7)
        Main_box.addWidget(self.Controller(), 1)

        self.scrollArea = QScrollArea()
        self.setCentralWidget(self.scrollArea)

        central_widget = QWidget()
        central_widget.setLayout(Main_box)
        self.scrollArea.setWidget(central_widget)
        self.scrollArea.setWidgetResizable(True) 

        apply_stylesheet(self.app, theme='light_cyan.xml')
        self.setWindowTitle('초해상도 기기')
        self.setWindowIcon(QIcon('Title.png'))
        self.setGeometry(0, 0, 768, 320)
        self.show()

    def Original_Video(self):
        main_screen_widget = QWidget(self)

        main_screen_layout = QVBoxLayout(main_screen_widget)

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 256, 256)  # Set the QLabel size to fit the new window size
        main_screen_layout.addWidget(self.label)

        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_video)
        main_screen_layout.addWidget(self.play_button)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        return main_screen_widget
    

    def play_video(self):
        if self.cap:
            self.cap.release()
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
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

    def closeEvent(self, event):
        self.cap.release()

    def Predict_Video(self):
        main_screen_widget = QWidget(self)

        main_screen_layout = QVBoxLayout(main_screen_widget)

        self.label_p = QLabel(self)
        self.label_p.setGeometry(10, 10, 256, 256)  
        main_screen_layout.addWidget(self.label_p)

        self.play_button_p = QPushButton('Play', self)
        self.play_button_p.clicked.connect(self.play_video_p)
        main_screen_layout.addWidget(self.play_button_p)

        self.cap_p = None
        self.timer_p = QTimer()
        self.timer_p.timeout.connect(self.update_frame_p)
        return main_screen_widget

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


    def closeEvent(self, event):
        self.cap_p.release()


    def Controller(self):
        Load_Image_widget = QWidget(self)

        self.Load_button = QPushButton('Load File', self)
        self.Load_button.setFixedSize(button_size_x, button_size_y) 
        self.Load_button.setStyleSheet(hover_style)
        self.Load_button.clicked.connect(self.Load_Video)

        self.Predict_button = QPushButton('Predict', self)
        self.Predict_button.setFixedSize(button_size_x, button_size_y) 
        self.Predict_button.setStyleSheet(hover_style)
        self.Predict_button.clicked.connect(self.Predict_image)

        self.Delete_button = QPushButton('Delete', self)
        self.Delete_button.setFixedSize(button_size_x, button_size_y) 
        self.Delete_button.setStyleSheet(hover_style)
        self.Delete_button.clicked.connect(self.Delete_image)

        self.progress_bar_label = QLabel('진행상황', self) 
        self.progress_bar = QProgressBar(self) 

        AGV_state_layout = QVBoxLayout(Load_Image_widget)
        AGV_state_layout.addWidget(self.Load_button)
        AGV_state_layout.addWidget(self.Predict_button)
        AGV_state_layout.addWidget(self.Delete_button)
        AGV_state_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)) 
        AGV_state_layout.addWidget(self.progress_bar_label)  
        AGV_state_layout.addWidget(self.progress_bar)
        AGV_state_layout.addStretch(1)

        Load_Image_widget.setLayout(AGV_state_layout)
        return Load_Image_widget
    
####
    def Load_Video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, 'Open file', 
                                                         './', "Video Files (*.mp4 *.avi *.mov)")
        if self.video_path:
            QMessageBox.information(self, "알림", f"비디오 경로가 갱신되었습니다: {self.video_path}")
        else:
            QMessageBox.warning(self, "알림", "비디오 파일을 선택하지 않았습니다.")

    def Predict_image(self):
        if self.video_path:
            detector = Superresolution_model()
            detector.detect_objects_in_video_and_save_frames(self.video_path, 
                                                             self.update_progress)
            QMessageBox.warning(self, "알림", "예측이 완료되었습니다.")
        else:
            QMessageBox.warning(self, "알림", "비디오 파일이 로드되지 않았습니다.")


    def Delete_image(self):
        self.label.clear()
        self.label_p.clear()
        self.progress_bar.reset()

app = QApplication(sys.argv)
execute_instance = Improve_resolution(app)
app.exec()