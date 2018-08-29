FROM ubuntu:16.04

RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get update && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
    mercurial \
    libav-tools \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev \
    libsmpeg-dev \
    libsdl1.2-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libplib-dev \
    libopenal-dev \
    libalut-dev \
    libvorbis-dev \
    libxxf86vm-dev \
    libxmu-dev \
    libgl1-mesa-dev \
    python3.7 \
    python3.7-tk \
    git

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --upgrade pip

ENV PYTHONPATH /usr/local/lib/python3.7/dist-packages
ENV DISPLAY=docker.for.mac.localhost:0
RUN python3.7 -m pip install numpy
RUN python3.7 -m pip install scipy
RUN python3.7 -m pip install tqdm
RUN python3.7 -m pip install pygame
RUN python3.7 -m pip install matplotlib

WORKDIR /root/maze_pro
ADD . /root/maze_pro
