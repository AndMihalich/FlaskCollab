FROM python:3.12.1

ENV FLASK_APP=collab.py
ENV FLASK_CONFIG=docker

WORKDIR /home/collab

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN python -m pip install -r requirements.txt


COPY app app
COPY migrations migrations
COPY collab.py config.py boot.sh ./

RUN chmod +x boot.sh

RUN useradd -m collab
RUN chown -R collab:collab /home/collab
USER collab

EXPOSE 8000
ENTRYPOINT ["./boot.sh"]