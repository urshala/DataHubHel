FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt setup.cfg setup.py ./

RUN pip install -r requirements.txt
