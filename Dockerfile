FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY *.py ./
COPY *.sh ./

ARG type=python
ARG command=sourceManager.py
ARG parameter1=fetch
ARG parameter2=
ARG parameter3=
ARG parameter4=
ARG parameter5=
ARG parameter6=
ARG parameter7=
ARG parameter8=
ARG parameter9=

CMD [ $type, $command, $parameter1, $parameter2, $parameter3, $parameter4, $parameter5, $parameter6, $parameter7, $parameter8, $parameter9 ]