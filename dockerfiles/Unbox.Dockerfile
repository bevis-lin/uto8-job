FROM python:latest

WORKDIR /Users/bevis/code/uto8-job/

RUN pip3 install web3
RUN pip3 install pika

COPY src ./

CMD [ "python", "Unbox.py"]