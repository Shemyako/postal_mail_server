#!/usr/bin/env python
import pika
import logging
import json
from aiogram import Bot, Dispatcher, types
import config
import db
import asyncio
from sqlalchemy import insert, select, and_
from datetime import datetime

from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL) 

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TG_TOKEN)

connection = pika.BlockingConnection(pika.URLParameters(
    "amqp://guest:guest@rabbitmq/"))
channel = connection.channel()
channel.queue_declare(queue='mails', durable=True)

print( ' [*] Waiting for messages. To exit press CTRL+C')

async def sending_messages(a, i):
    i = i.split("@")
    await bot.send_message(i[0], f"F:{a.get('from')}\nT:{i[1]}\nS:{a.get('subject')}\nD:{a.get('date')}\n{a.get('text')}")


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
                    res = dict(*res)
                    await db.database.execute(query, {
                        "mail":res["id"], 
                        "text":a["text"] if len(a["text"]) < 250 else a["text"][:250], 
                        "from_user":i[0], 
                        "date":datetime.strptime(a["date"],"%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
                    })

                    # print(res)
                    to.append(str(res["owner"]) + "@" + i[0])

    await db.database.disconnect()
    if to:
        tasks = [asyncio.ensure_future(sending_messages(a, i)) for i in to]
        await asyncio.wait(tasks)

    return
    # print( " [x] Received %r" % (a,))
    # print(a["text"])
    # ch.basic_ack(delivery_tag = method.delivery_tag)


def main(ch, method, properties, body):
    global loop
    loop.run_until_complete(callback(ch, method, properties, body))
    # asyncio.run(callback(ch, method, properties, body))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_message_callback=main,
                      queue='mails',
                      auto_ack=True)

channel.start_consuming()