FROM python:3.10-slim-bullseye

# Set labels 
LABEL vendor=SINTEF_Digital \
      SINDIT.is-beta=True\
      SINDIT.version="0.0.1-beta" \
      SINDIT.release-date="2022-07-12"

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

COPY . .

RUN apt-get update

RUN apt-get install -y curl

# git required for the pke keyphrase extraction library (git pip link)
RUN apt-get install -y git

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# libgl required for CAD module
RUN apt-get install -y libgl1

# required for textract (PDF text extraction) (but removed pstotext because it is no longer available!)
RUN apt-get install -y python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig

# gcc required for tsfresh (timeseries feature extractor)
# tsfresh installation only works with the dependency (unlike the ones for other packages)
RUN apt-get install -y gcc
RUN pip install tsfresh

RUN apt-get clean

# Requirements for the pke keyphrase extraction library
RUN python -m spacy download en_core_web_sm

EXPOSE 8050
EXPOSE 8000

# ENTRYPOINT ["python", "/opt/sindit/main.sh" ]







