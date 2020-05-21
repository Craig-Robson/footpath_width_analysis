FROM python:3.7
RUN apt-get -y update \
    && apt-get -y install libspatialindex-dev
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN pip install centerline configparser
COPY functions.py /
COPY run.py /
