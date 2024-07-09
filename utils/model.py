import os
import cv2
import numpy as np
import torch
import segmentation_models_pytorch as smp

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

class SuperresolutionModel:
    def __init__(self):
        self.model = smp.UnetPlusPlus(encoder_name="efficientnet-b7", 
                                      encoder_weights=None, 
                                      in_channels=3, 
                                      classes=3).to(device)

        self.model.load_state_dict(torch.load("./best_model_b7_3.pth")) # 이것은 Restart-Copy1 파일로 만든 모델
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

        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        video_writer = cv2.VideoWriter("Resolution_improved_vid.mp4", fourcc, frame_rate, (width, height))
        for image in images:
            img_path = os.path.join(output_dir, image)
            frame = cv2.imread(img_path)
            video_writer.write(frame)

        video_writer.release()