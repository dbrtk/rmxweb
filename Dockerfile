FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends \
	build-essential \
	python3-dev \
	python3-venv \
	python3-setuptools \
	python3-pip \
	nginx \
	ca-certificates \
    && apt-get -y autoremove && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/*

COPY rmxweb /opt/program/rmxweb
COPY conf/nginx/nginx.conf /opt/program

# chmod perms on executables
RUN chmod +x /opt/program/rmxweb/serve
RUN ln -s /opt/program/rmxweb/serve /usr/local/bin/serve

COPY celery.sh /opt/program
# COPY celery_worker.py /opt/program

COPY requirements.txt /opt/program

RUN python3 -m pip install --upgrade pip && \
	python3 -m pip install -r /opt/program/requirements.txt

WORKDIR /opt/program

# environment variables

# the endpoint for extractxt
ENV EXTRACTXT_ENDPOINT 'http://extractxt:8003'

# the data root
ENV DATA_ROOT '/data'
# the tmp dir for rmxbot
ENV TMP_DATA_DIR '/tmp'

