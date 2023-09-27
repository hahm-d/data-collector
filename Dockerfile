FROM python:3.9

WORKDIR /onna_data_collector

ENV PYTHONUNBUFFERED=0

COPY . /onna_data_collector/

RUN pip install --no-cache-dir -r requests

CMD [ "python", "main.py"]