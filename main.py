# Copyright 2014-2021 The aiosmtpd Developers
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import email
import base64

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Sink

class RelayHandler:
    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        
        # Попробовать без splitlines()
        # for ln in envelope.content.decode('utf8', errors='replace').splitlines():
        #     print(f'> {ln}'.strip())

        # print(envelope.content.decode('utf8', errors='replace'))
        # print('------------------...--------------------')
        
        msg = email.message_from_bytes(envelope.original_content)

        # print(msg)

        # print([i.get_content_type() for i in msg.walk()])
        for part in msg.walk():
            if part.get_content_maintype() == 'text':# and part.get_content_subtype() == 'plain':
                # print(base64.b64decode(part.get_payload()).decode('latin-1', 'replace'))
                
                # print()
                print(base64.b64decode(part.get_payload()).decode())

        print('End of message')
        return '250 Message accepted for delivery'


async def amain(loop):
    handler = RelayHandler()
    cont = Controller(
        handler,
        hostname='',
        port=25
    )
    cont.start()
    input("Server started. Press Return to quit.")
    cont.stop()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # try:
    loop.run_until_complete(amain(loop=loop))
    
    # loop.create_task(amain(loop=loop))
    # loop.run_forever()
    # except KeyboardInterrupt:
    #     print("User abort indicated")



