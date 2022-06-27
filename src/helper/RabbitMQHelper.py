"""myRabbit - RabbitMQ Helper"""
import pika
import os

credentials = pika.PlainCredentials('uto8','uto8')


def QueueDeclare(name):
  connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['RABBITMQ_HOST'],5672,'/',credentials))
  channel = connection.channel()
  channel.queue_declare(queue=name)
  connection.close()

def Publish(queueName, message):
  connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['RABBITMQ_HOST'],5672,'/',credentials))
  channel = connection.channel()
  channel.basic_publish(exchange='', routing_key=queueName, body=message)
  print(" [x] Sent "+message)
  connection.close()
