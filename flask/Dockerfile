FROM python:3.8-slim-buster

WORKDIR /flask

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /flask

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
