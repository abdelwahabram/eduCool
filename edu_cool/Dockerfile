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

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

RUN npm run msbundle

CMD [ "python3", "manage.py", "runserver" , "0.0.0.0:8000"]

# fell into dependency hell for a while but 've handled it
