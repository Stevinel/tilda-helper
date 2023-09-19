FROM python:3.10.0-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USER stan
ENV GROUP admin
ENV WORK_DIR "/usr/src/app"

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev zlib-dev jpeg-dev libffi-dev

RUN mkdir -p ${WORK_DIR}
WORKDIR ${WORK_DIR}

RUN addgroup --system ${GROUP} &&\
    adduser --system --home ${WORK_DIR}/../user --ingroup ${GROUP} ${USER} --shell /bin/bash &&\
    chown -R ${USER}:${GROUP} ${WORK_DIR}/..

COPY requirements.txt .
COPY entrypoint.sh .


RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod +x /usr/src/app/entrypoint.sh

COPY . .

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]