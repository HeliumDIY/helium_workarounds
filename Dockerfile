FROM python:3.7-alpine

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY src/ /app
WORKDIR /app

RUN mkdir /log

VOLUME ["/log"]

CMD ["python3", "fix_not_found_peer.py", "/log/console.log"]