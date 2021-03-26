FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY configs /app/configs
COPY data /app/data
COPY tests /app/tests
COPY build_clinician_mart.py /app
