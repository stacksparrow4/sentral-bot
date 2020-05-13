FROM python:3.8

RUN mkdir /root/bot
WORKDIR "/root/bot"

COPY requirements.txt getmessages.py discordclient.py ./

RUN pip install -r requirements.txt

CMD [ "python", "./discordclient.py" ]
