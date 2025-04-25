FROM python:3.12.3

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /RetailCRM_task

COPY . .

RUN pip install -r requirements.txt
