FROM python:3.8-slim-buster

WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ss_utils.py ss_utils.py
COPY cb_usd.py cb_usd.py
COPY main.py main.py
COPY db_utils.py db_utils.py
COPY creds.json creds.json

CMD ["python", "-u", "main.py"]