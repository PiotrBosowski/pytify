FROM python:latest
MAINTAINER Piotr Bosowski "piotr.bosowski@gmail.com"

WORKDIR /home

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . ./

CMD [ "python", "./webserver.py" ]
