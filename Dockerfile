FROM python:3.10-alpine

RUN adduser -D tdtonline

WORKDIR /home/tdtonline
ENV http_proxy=
COPY requirements.txt requirements.txt
COPY libudfdll.so libudfdll.so
COPY .env .env
RUN python -m pip install --upgrade pip
RUN python -m venv venv
RUN apk update && \
  apk add --no-cache libc6-compat && \
  ln -s /lib/libc.musl-x86_64.so.1 /lib/ld-linux-x86-64.so.2
RUN apk add gcc musl-dev libffi-dev openssl-dev python3-dev g++
RUN pip3 install greenlet
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
# COPY migrations migrations
COPY run.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP run.py

RUN chown -R tdtonline:tdtonline ./
USER tdtonline

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
