FROM python:alpine

RUN apk add --update --no-cache bash

RUN apk add --update --no-cache nodejs

RUN apk add --update --no-cache npm

WORKDIR /app

COPY requirements.txt  /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY package.json  /app/

RUN npm install

COPY . /app/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

RUN npm run msbundle

ADD entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]