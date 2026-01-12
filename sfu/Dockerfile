FROM node:24-alpine

RUN apk add --update --no-cache bash

RUN apk add --update --no-cache linux-headers

RUN apk add --update --no-cache build-base

RUN apk add --update --no-cache g++

RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python

RUN apk add --update --no-cache py3-pip


WORKDIR /app

COPY package.json  /app/

RUN npm install

COPY . /app/