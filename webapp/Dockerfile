FROM ubuntu:latest

RUN groupadd --system falcon
RUN useradd --system -g falcon falcon

RUN apt-get update
RUN apt-get dist-upgrade -y
RUN apt-get install -y \
    build-essential \
    libev-dev \
    libpython3-dev \
    python3 \
    python3-distutils \
    wget

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py

RUN python3 -m pip install --upgrade --no-cache-dir \
    bjoern \
    falcon \
    pip

COPY app app

CMD ["python3", "-u", "app/main.py"]
