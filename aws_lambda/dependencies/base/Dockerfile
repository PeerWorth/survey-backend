FROM public.ecr.aws/lambda/python:3.11 AS builder

RUN yum install -y zip && yum clean all

RUN pip install --upgrade pip

WORKDIR /var/task

COPY requirements.txt .

RUN mkdir -p python && \
    pip install -r requirements.txt -t python/

RUN zip -r layer.zip python/
