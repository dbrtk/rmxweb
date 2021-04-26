FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
	build-essential \
	python3-dev \
	python3-venv \
	python3-setuptools \
	python3-pip \
	ca-certificates \
    && apt-get -y autoremove && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

COPY rmxweb /opt/program/rmxweb

COPY requirements.txt /opt/program

RUN python3 -m pip install --upgrade pip && \
	python3 -m pip install -r /opt/program/requirements.txt

# setting up /opt/program as working directory
WORKDIR /opt/program/rmxweb

# run migrations on the databases
RUN python3 manage.py makemigrations data ; \
    python3 manage.py makemigrations container \
    && python3 manage.py migrate

# environment variables

# the endpoint for extractxt
ENV EXTRACTXT_ENDPOINT 'http://extractxt:8003'

# the data root
ENV DATA_ROOT '/data'
# the tmp dir for rmxweb
ENV TMP_DATA_DIR '/tmp'

ENV TEMPLATES_FOLDER '/opt/program/templates'

ENV STATIC_FOLDER '/var/www/rmx'

