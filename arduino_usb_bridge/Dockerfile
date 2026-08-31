ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest

FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

RUN pip3 install --no-cache-dir pyserial requests

COPY run.py /run.py

CMD ["python3", "/run.py"]
