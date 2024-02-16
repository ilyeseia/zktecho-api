# -*- coding: utf-8 -*-
import os
import sys
import pika
import json

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)

from zk import ZK


# RabbitMQ server connection parameters
rabbitmq_host = 'kangaroo.rmq.cloudamqp.com'
rabbitmq_port = 5672   # Default RabbitMQ port
rabbitmq_user = 'zgzvgnoe'
rabbitmq_password = 'v29I1D0v0Q0rAZVYqrwWCjS8oy2fELIx'
rabbitmq_vhost = 'zgzvgnoe'

# Create connection parameters
credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
parameters = pika.ConnectionParameters(
    host=rabbitmq_host,
    port=rabbitmq_port,
    virtual_host=rabbitmq_vhost,
    credentials=credentials
)

def serialize_attendance(attendance):
    return {
        "employeId": attendance.user_id,
        "timestamp": attendance.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "status": attendance.status,
        "punch": attendance.punch
    }

conn = None
zk = ZK('10.1.5.8', port=4370)
try:
    conn = zk.connect()
    for attendance in conn.live_capture():
        if attendance is None:
            pass
        else:
            serialize_attendances = [serialize_attendance (attendance)]
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue='pointeuse8')
            channel.basic_publish(exchange='', routing_key='pointeuse8', body= json.dumps(serialize_attendances))
            connection.close()  
            print (serialize_attendances)
except Exception as e:
    print ("Process terminate : {}".format(e))
finally:
    if conn:
        conn.disconnect()