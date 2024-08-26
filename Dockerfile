
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu18.04

RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-venv \
    python3.8-distutils \
    python3-pip \
    bash

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

WORKDIR /app

RUN python3 -m venv bird_resol_up && \
    . bird_resol_up/bin/activate && \
    pip install --upgrade pip && \
    pip install segmentation-models-pytorch albumentations scikit-learn opencv-python tqdm && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip install six

COPY . /app

ENTRYPOINT ["/bin/bash"]