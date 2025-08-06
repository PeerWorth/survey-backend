FROM public.ecr.aws/sam/build-python3.11:latest

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install \
        --only-binary=:all: \
        --target=python \
        -r requirements.txt

RUN zip -r layer.zip python/
