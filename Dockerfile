FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY src/ /app
WORKDIR /app

RUN mkdir /log

VOLUME ["/log"]
ENV LOG_FILE /log/console.log
ENV PYTHONUNBUFFERED 1

CMD ["python3", "fix_not_found_peer.py"]