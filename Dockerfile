FROM python:latest
MAINTAINER Piotr Bosowski "piotr.bosowski@gmail.com"

WORKDIR /home

RUN apt update && apt install -y ffmpeg

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . ./

CMD [ "python", "./webserver.py" ]
