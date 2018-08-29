#!/bin/bash

apt-get update && apt-get install -y software-properties-common
apt-get update && add-apt-repository ppa:deadsnakes/ppa
apt-get update && apt-get install -y \
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

apt-get update && apt-get install -y python3-pip
pip3 install --upgrade pip

export DISPLAY=docker.for.mac.localhost:0
python3.7 -m pip install numpy
python3.7 -m pip install scipy
python3.7 -m pip install tqdm
python3.7 -m pip install pygame
python3.7 -m pip install matplotlib

