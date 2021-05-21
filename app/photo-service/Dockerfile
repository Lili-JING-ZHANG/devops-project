FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY . .
ENV MODULE_NAME=photo_service
ENV LOG_LEVEL=info
ENV GRACEFUL_TIMEOUT=10
RUN python3 -m pip install --upgrade pip
RUN pip3 install --no-cache-dir --trusted-host pypi.python.org mongoengine requests Pillow python-multipart protobuf grpcio



