# Superresolution 애플리케이션 시연

## 1. 시연

<img src="https://github.com/bloodmage1/SuperResol_box/blob/main/Demonstration/home_capture.png"/>

실행했을 시 첫화면이다.

---
<img src="https://github.com/bloodmage1/SuperResol_box/blob/main/Demonstration/img_loaded.png"/>

원하는 영상을 불러올 수 있다. 현재 업로드된 사용할 수 있는 파일은 videoo 폴더 안의 새 영상 3개다.

---

<img src="https://github.com/bloodmage1/SuperResol_box/blob/main/Demonstration/img_predicted.png"/>

predict 버튼을 클릭하여 주어진 모델을 이용해, Resolution_improved_vid.mp4 파일을 생성할 수 있다. 이 파일은 무게가 약 267MB라 github에 올리지 못하지만, 만드는 과정을 보여주는 코드가 Restart-Copy1.ipynb에 저장되어 있다.

---
<img src="https://github.com/bloodmage1/SuperResol_box/blob/main/Demonstration/superresolution_result.gif"/>

predict한 파일을 재생할 수 있다. 

## 2. 개발환경

- Window OS, Window 11
- Python 3.8.7
- PySide6

## 3. 디렉토리 구조

```
Superresolution/
│
├── main.py
├── ui/
│   ├── main_screen.py
│   ├── original_video.py # predict_video와 합쳐도 됨
│   ├── predict_video.py
│   └── controller.py
└── utils/
    ├── model.py
```
  
## 4. 각 함수의 기능 설명
 
### Superresolution_model 클래스

- def detect_objects_in_video_and_save_frames

  - 비디오 파일을 열고, 프레임을 처리하여 초해상도 비디오를 생성합니다.
  - 각 프레임을 처리하고, 프레임별로 예측 이미지를 저장합니다.
  - 진행 상황을 업데이트하기 위해 progress_callback을 호출합니다.
  - 모든 프레임 처리가 완료되면, 이미지를 비디오 파일로 저장합니다.
  
### ImproveResolution 클래스

- def update_progress
  - 진행 상황을 업데이트하여 프로그레스 바에 반영합니다.

- def UI초기화
  - 메인 레이아웃을 설정하고, 원본 비디오와 예측 비디오를 표시할 위젯 및 컨트롤러를 추가합니다.
  - 스크롤 영역을 설정하고, 테마를 적용합니다.
  - 윈도우의 제목과 아이콘을 설정하고, 창의 크기를 설정한 후 창을 표시합니다.

### OriginalVideo 클래스
- 원본 비디오를 표시할 위젯을 생성하고 반환합니다.
- 비디오 표시를 위한 QLabel과 비디오 재생을 위한 재생 버튼을 설정합니다.
- 비디오 캡처 객체와 비디오 프레임을 업데이트하기 위한 타이머를 초기화합니다.

- def play_video
  - 기존의 비디오 캡처 객체를 해제합니다.
  - video_path에 지정된 비디오 파일을 열고 프레임을 업데이트하기 위한 타이머를 시작합니다.
  - 비디오 파일이 로드되지 않은 경우 경고를 표시합니다.

- def update_frame
  - 비디오 캡처 객체에서 프레임을 읽어옵니다.
  - 프레임을 크기 조정하고 QImage로 변환하여 QLabel을 업데이트하여 프레임을 표시합니다.
  - 비디오가 끝나면 타이머를 중지하고 비디오 캡처 객체를 해제합니다.


### PredictVideo 클래스
- 예측 비디오를 표시하는 위젯을 생성하고 반환합니다.
- 비디오 표시를 위한 QLabel과 예측 비디오 재생을 시작하는 재생 버튼을 설정합니다.
- 예측 비디오 프레임을 업데이트하기 위한 비디오 캡처 객체와 타이머를 초기화합니다.

- def play_video_p
  - 기존의 예측 비디오 캡처 객체를 해제합니다.
  - 예측 비디오 파일을 열고 프레임을 업데이트하기 위한 타이머를 시작합니다.

- def update_frame_p
  - 예측 비디오 캡처 객체에서 프레임을 읽어옵니다.
  - 프레임을 크기 조정하고 QImage로 변환하여 QLabel을 업데이트하여 프레임을 표시합니다.
  - 예측 비디오가 끝나면 타이머를 중지하고 비디오 캡처 객체를 해제합니다.

### Controller 클래스
- 컨트롤 버튼(파일 로드, 예측, 삭제)이 있는 위젯을 생성하고 반환합니다.
- 컨트롤 버튼의 레이아웃과 스타일을 설정합니다.
- 버튼을 해당 메서드(Load_Video, Predict_image, Delete_image)에 연결합니다.

- def load_video
  - 파일 대화 상자를 열어 비디오 파일을 선택하고 video_path를 업데이트합니다.
  - 비디오 경로가 업데이트되었음을 나타내는 메시지를 표시합니다.
  - 파일을 선택하지 않은 경우 경고를 표시합니다.

- def predict_image
  - Superresolution 모델을 사용하여 video_path에 지정된 비디오 파일에서 객체 감지를 수행합니다.
  - 예측이 완료되었음을 나타내는 메시지를 표시합니다.
  - 비디오 파일이 로드되지 않은 경우 경고를 표시합니다.

- def delete_image
  - 원본 및 예측 비디오를 표시하는 QLabel을 지웁니다.
  - 프로그레스 바를 초기화합니다.



