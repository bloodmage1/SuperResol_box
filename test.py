import argparse
import os
import cv2
import torch
import numpy as np
import segmentation_models_pytorch as smp
from tqdm import tqdm

# 필요한 인자들을 받아오기 위한 ArgumentParser 설정
parser = argparse.ArgumentParser()
parser.add_argument('--classes_names_dict', type=str, help='클래스 이름과 번호 매핑')
parser.add_argument('--dataset', type=str, help='비디오 파일 경로') ##
parser.add_argument('--weights', type=str, help='모델 가중치 파일 경로') ##
parser.add_argument('--save_dir', type=str, help='결과 저장 디렉토리 경로')
parser.add_argument('--patch_size', type=int, help='패치 크기', default=96) ##
parser.add_argument('--resize', type=int, help='이미지 리사이즈 크기', default=256) ##
parser.add_argument('--individual', type=int, help='개별 처리 여부', default=1)
ARGS = parser.parse_args()

'''
source bird_resol_up/bin/activate

python3 test.py\
    --classes_names_dict "{'bird': 1, 'fish': 2}"\
    --dataset "./videoo/"\
    --weights "./model/best_model_b7_3.pth"\
    --save_dir "./test_result/"\
    --patch_size 96\
    --resize 256\
    --individual 1

'''

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Superresolution_model:
    def __init__(self):
        self.model = smp.UnetPlusPlus(encoder_name="efficientnet-b7", 
                                encoder_weights=None, 
                                in_channels=3, 
                                classes=3).to(device)

        self.model.load_state_dict(torch.load(ARGS.weights, map_location=device))
        self.model.eval()

    def detect_objects_in_video_and_save_frames(self, video_path, 
                                                progress_callback, 
                                                output_dir, 
                                                frame_rate=10):
        video_files = [f for f in os.listdir(video_path) if f.endswith(('.mp4'))]

        cap = cv2.VideoCapture(os.path.join(video_path, video_files[0]))
        frame_count = 0
        patch_size = ARGS.patch_size
        stride = int(patch_size / 2)
        batch_size = 1

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        total = np.zeros(shape=(total_frames, ARGS.resize, ARGS.resize, 3))

        while cap.isOpened():
            
            print()
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.resize(frame, (ARGS.resize, ARGS.resize))
            img = frame / 255
        
            crop = []
            position = []
            batch_count = 0
            
            result_img = np.zeros(shape=(img.shape[0], img.shape[1], 3))
            voting_mask = np.zeros(shape=(img.shape[0], img.shape[1], 3))

            for top in tqdm(range(0, img.shape[0], stride)):
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
            # print(f"output_dir:{output_dir}")
            rgb_image = (total[frame_count] * 255).astype(np.uint8)
            cv2.imwrite(frame_filename, rgb_image)

            frame_count += 1
            progress_callback(frame_count, total_frames)
        
        cap.release()
        images = [img for img in os.listdir(output_dir) if img.endswith(".png")]
        images.sort() 

        first_frame_path = os.path.join(output_dir, images[0])
        frame = cv2.imread(first_frame_path)
        height, width, _ = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        video_writer = cv2.VideoWriter(os.path.join(output_dir, "Resolution_improved_vid.mp4"), fourcc, frame_rate, (width, height))
        for image in images:
            img_path = os.path.join(output_dir, image)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()

def progress_callback(frame_count, total_frames):
    print(f"Processed frame {frame_count}/{total_frames}")

# 실행 부분
if __name__ == "__main__":
    model = Superresolution_model()
    model.detect_objects_in_video_and_save_frames(ARGS.dataset, 
                                                  progress_callback, 
                                                  ARGS.save_dir, 
                                                  frame_rate=10)
