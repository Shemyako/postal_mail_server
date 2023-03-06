#!/usr/bin/env python
import pika
import logging
import json
from aiogram import Bot, Dispatcher, types
import config
import db
import asyncio

from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL) 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TG_TOKEN)

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='mails', durable=True)

print( ' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    a = json.loads(body)

    await db.database.connect()
    to = []
    for i in a["to"]:
            i = i.split("@")
            if i[1] == config.MAIL_DOMEN:
                res = await db.database.fetch_all(
                    db.mails.select().where(
                        and_(
                            i[0]==db.mails.c.name, 
                            db.mails.c.is_active==True
                        )
                    )
                )
                # print(res)
                
                if res != []:
                    query = insert(db.messages)
                    await db.database.execute(query, {
                        "mail":res["id"], 
                        "text":a["text"], 
                        "from_user":i[0], 
                        "date":datetime.strptime(a["date"],"%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                    })

                    res = dict(*res)
                    # print(res)
                    to.append(str(res["owner"]) + "@" + i[0])

    await db.database.disconnect()
    # print(to)
    for i in to:
        i = i.split("@")
        await bot.send_message(i[0], f"F:{a.get('from')}\nT:{i[1]}\nS:{a.get('subject')}\nD:{a.get["date"]}\n{a.get('text')}")


    # print( " [x] Received %r" % (a,))
    # print(a["text"])
    # ch.basic_ack(delivery_tag = method.delivery_tag)


def main(ch, method, properties, body):
    asyncio.run(callback(ch, method, properties, body))

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=main,
                      queue='mails',
                      auto_ack=True)

channel.start_consuming()