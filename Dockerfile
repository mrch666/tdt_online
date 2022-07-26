FROM python:3.6-alpine

RUN adduser -D tdtonline

WORKDIR /home/tdtonline

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
# COPY migrations migrations
COPY tdtonline.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP tdtonline.py

RUN chown -R tdtonline:tdtonline ./
USER tdtonline

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
