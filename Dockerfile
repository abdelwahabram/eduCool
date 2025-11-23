FROM python

RUN mkdir /app

WORKDIR /app

COPY requirements.txt  /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD [ "python3", "edu_cool/manage.py", "runserver" , "0.0.0.0:8000"]

RUN python3 edu_cool/manage.py makemigrations
RUN python3 edu_cool/manage.py migrate
