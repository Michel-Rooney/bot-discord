FROM ubuntu:latest

WORKDIR /home/ubuntu

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git python3 python3-pip python3-venv

RUN git clone https://github.com/Michel-Rooney/bot-discord

WORKDIR /home/ubuntu/bot-discord/bot-all

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["bash", "-c", ". venv/bin/activate && python man.py"]
