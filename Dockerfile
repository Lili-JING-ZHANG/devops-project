FROM python:3.7
CMD mkdir data
WORKDIR /data
CMD ["python3","-m","http.server","8080"]
