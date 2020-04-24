FROM python:3

ADD . /code

RUN pip install -r requirements.txt

WORKDIR /code

CMD python3 main.py