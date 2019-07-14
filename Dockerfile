FROM python:3.7
MAINTAINER Bartosz
ENV PYTHONBUFFERED 1
RUN mkdir /my_wallet
WORKDIR /my_wallet
COPY requirements.txt /my_wallet/
ADD requirements /my_wallet/requirements/
RUN pip install -r requirements.txt
COPY . /my_wallet/