# to build: docker build -t onna-data-collector .
# to run: docker run -p 4000:80 onna-data-collector
# confirm running on terminal (docker ps) or docker desktop
FROM python:3.9

ENV PYTHONUNBUFFERED True

WORKDIR /onna_data_collector

COPY . /onna_data_collector

# run this before copying requirements for cache efficiency
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 80

CMD [ "python", "main.py"]