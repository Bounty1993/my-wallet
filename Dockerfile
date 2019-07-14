FROM python:3.7
MAINTAINER Bartosz
ENV PYTHONBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
ADD requirements /code/requirements/
RUN pip install -r requirements.txt
COPY . /code/