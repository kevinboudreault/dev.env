FROM python:3.12-slim

WORKDIR /app
RUN pip install pyzmq

COPY publisher.py .
CMD ["python", "publisher.py"]
