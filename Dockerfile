FROM python:3.12.5-alpine3.19

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT [ "sh" ]
CMD [ "-c", "while true ; do sleep 60 ; done" ]
