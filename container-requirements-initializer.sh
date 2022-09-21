#!/bin/bash


apt-get update

apt-get install -y curl wget

# git required for the pke keyphrase extraction library (git pip link)
apt-get install -y git

pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# libgl required for CAD module
apt-get install -y libgl1

# required for textract (PDF text extraction) (but removed pstotext because it is no longer available!)
apt-get install -y python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig

# gcc required for tsfresh (timeseries feature extractor)
# tsfresh installation only works with the dependency (unlike the ones for other packages)
apt-get install -y gcc
pip install tsfresh

# Influx cli for remote backup / restore
wget https://dl.influxdata.com/influxdb/releases/influxdb2-client-2.4.0-amd64.deb
apt install ./influxdb2-client-2.4.0-amd64.deb
rm influxdb2-client-2.4.0-amd64.deb

apt-get clean

# Requirements for the pke keyphrase extraction library
python -m spacy download en_core_web_sm

# OpenMMLab (must be after the pip requirements for mim)
# RUN mim install mmcv-full

pip install torch==1.12.1+cpu torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cpu/torch1.12.0/index.html

# RUN pip install mmdet
cd dependencies

if [ ! -d "./mmdetection" ]
then
    git clone https://github.com/open-mmlab/mmdetection.git
else
    git pull
fi

cd mmdetection
pip install -v -e .
cd ..