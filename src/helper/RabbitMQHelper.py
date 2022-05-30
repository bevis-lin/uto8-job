"""myRabbit - RabbitMQ Helper"""
import pika
import os

credentials = pika.PlainCredentials('uto8','uto8')
connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ['RABBITMQ_HOST'],5672,'/',credentials))
channel = connection.channel()

def QueueDeclare(name):
  channel.queue_declare(queue=name)

def Publish(queueName, message):
  channel.basic_publish(exchange='', routing_key=queueName, body=message)
  print(" [x] Sent "+message)

