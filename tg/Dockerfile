FROM python:3.8-slim-buster

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY bot.py bot.py
COPY users.txt users.txt

CMD ["python3", "bot.py"]
