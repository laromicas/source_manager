FROM python:3-slim

WORKDIR /usr/src/app

RUN  apt-get update \
    && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY *.py ./
COPY *.sh ./

RUN chmod +x *.py
RUN chmod +x *.sh

CMD [ "./up.sh" ]