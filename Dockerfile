FROM python:2

ADD . /ursula

WORKDIR /ursula

RUN pip install -r requirements.txt

RUN mkdir /root/.ssh

CMD test/setup && test/run deploy
