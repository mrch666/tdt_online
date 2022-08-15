FROM python:3.10-alpine

RUN adduser -D tdtonline

WORKDIR /home/tdtonline
ENV http_proxy=
COPY requirements.txt requirements.txt
COPY libudfdll.so libudfdll.so
COPY .env .env
RUN python -m pip install --upgrade pip
RUN python -m venv venv
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
