FROM ubuntu:latest

RUN groupadd --system falcon
RUN useradd --system -g falcon falcon

RUN DEBIAN_FRONTEND=noninteractive apt-get update > /dev/null
RUN DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -y > /dev/null
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    bind9-host \
    build-essential \
    libev-dev \
    libpq-dev \
    libpython3-dev \
    postgresql-client-12 \
    python3 \
    python3-distutils \
    wget > /dev/null

RUN wget --quiet https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py

RUN python3 -m pip install --upgrade --no-cache-dir \
    bjoern \
    falcon \
    pip \
    psycopg2

COPY app app

CMD ["python3", "-u", "app/main.py"]
