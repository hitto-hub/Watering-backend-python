# pythonのバージョンは適当
FROM python:3.10.12

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
