from logger import setup_logging
from message_handler import render_msg, parse_data
import asyncio
from random import randrange

log = setup_logging(__name__)


class ChatClient(asyncio.Protocol):
    message = 'This is the message. It will be echoed.'
    client = 'CLIENT{:0>3}'.format(randrange(0,1000))
    transport = None

    def connection_made(self, transport):
        self.transport = transport

        log.debug("Setting up connection!")

        # Do Register
        self.register()

        res = True
        while(res):
            res = self.send_msg()

        log.debug("Disconnecting from server!")
        self.transport.close()

    def data_received(self, data):
        mstring = data.decode()
        log.debug('Data received: [{}]'.format(mstring))

        pdata = parse_data(mstring)

        print("\t{src}> {msg}\n".format(src=pdata["src"], msg=pdata["msg"]))


    def connection_lost(self, exc):
        log.warning('Server closed the connection')
        asyncio.get_event_loop().stop()

    def register(self):
        data = render_msg(cmd="REG", client=self.client)
        self.transport.write(data.encode())
        log.debug("Regsitered with Server")

    def send_msg(self):
        target = input("ENTER CLIENT: ")
        message = input("ENTER MSG: ")

        data = render_msg(cmd="SND", client=target, msg=message)

        self.transport.write(data.encode())
        log.debug("Sending message to server! [{}]".format(data))

        ans = input("Continue? [y/n]: ")

        return True if ans.lower() == 'y' else False


loop = asyncio.get_event_loop()
coro = loop.create_connection(ChatClient, '127.0.0.1', 8888)

try:
    loop.run_until_complete(coro)
    loop.run_forever()
except KeyboardInterrupt:
    log.warning("Client exiting!")
except Exception as ex:
    log.exception("Exception in client! msg: {}".format(str(ex)))
finally:
    log.debug("Closing client!")
    loop.close()