#############
#Dockerfile to render objects in Blender
#Based on Ubuntu
#############
# Download image of Ubuntu 
FROM ubuntu
LABEL authors="Egor Budlov <budlow@yandex.ru>"
# Update
RUN apt-get update
# Install all necessary packages
RUN apt-get install sudo
RUN sudo apt install -y software-properties-common
RUN sudo add-apt-repository ppa:thomas-schiex/blender 
RUN apt-get update
RUN sudo apt-get install -y blender
RUN sudo apt-get install -y git
RUN apt-get install -y dos2unix
RUN apt install -y python3-pip
RUN sudo apt-get install -y libsm6 libxrender1 libfontconfig1
RUN pip3 install -y scikit-image
RUN pip3 install -y opencv-python
# Set working directory and clone a repository
RUN mkdir /bscript
WORKDIR /bscript
RUN git clone https://github.com/8-lines/blender_PBR
WORKDIR /bscript/blender_PBR/docker-container
RUN dos2unix linux-run.sh
CMD linux-run.sh