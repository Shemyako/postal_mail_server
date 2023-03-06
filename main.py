# Copyright 2014-2021 The aiosmtpd Developers
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import email
import base64
import pika
import json
from email.header import decode_header

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink

channel = None

class RelayHandler:
    async def handle_DATA(self, server, session, envelope):
        # print('Message from %s' % envelope.mail_from)
        # print('Message for %s' % envelope.rcpt_tos)
        # print('Message data:\n')

        message = {
            "to" : envelope.rcpt_tos,
            "from" : envelope.mail_from, 
            "subject" : "",
            "text" : "",
            "date" : ""
        }

        msg = email.message_from_bytes(envelope.original_content)
        # print(msg)
        # Проверяем тему и дату в письме. Если их нет, но письмо не рассматриваем
        if "Subject" in msg and "Date" in msg:
            message["subject"] =  (decode_header(msg["Subject"])[0][0].decode())
            message["Date"] = msg["Date"]
        else:
            return

        # Проходимся по письму и формируем текст для отправки
        for part in msg.walk():
            if part.get_content_maintype() == 'text' and part.get_content_subtype() == 'plain':
                # print(base64.b64decode(part.get_payload()).decode('latin-1', 'replace'))
                message["text"] += base64.b64decode(part.get_payload()).decode()

        # Добавляем в rabbitmq на обработку письмо
        channel.basic_publish(exchange='',
                      routing_key='mails',
                      body=json.dumps(message),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

        print('End of message')
        return '250 Message accepted for delivery'


async def amain(loop):
    global channel
    # соединяемся с rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='mails', durable=True)

    handler = RelayHandler()
    cont = Controller(
        handler,
        hostname='',
        port=25
    )
    cont.start()
    input("Server started. Press Enter to quit.")
    cont.stop()
    connection.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # try:
    loop.run_until_complete(amain(loop=loop))
    
    # loop.create_task(amain(loop=loop))
    # loop.run_forever()
    # except KeyboardInterrupt:
    #     print("User abort indicated")



