from message_handler import *
from logger import setup_logging

import asyncio
from itertools import count


# DEBUG STUFF
_d_conn_counter = 0  # Counter for conns.
_d_conn_rev = 0

# Logging
log = setup_logging(__name__)

# List of all connections
connections = {}


class ChatServer(asyncio.Protocol):
    name = None         # Name of client
    transport = None    # Transport i/f to 


    def connection_made(self, transport):
        global _d_conn_counter
        _d_conn_counter += 1
        
        host, port = transport.get_extra_info('peername')
        log.debug("Connection made from {1}:{2}. Total = {0}".format(_d_conn_counter, host, port))

        # Storing this connection...
        self.transport = transport

    def data_received(self, data):
        log.debug("Data received from {0}: [{1}]".format(self.name, data.decode()))

        # Process data
        self._process_data(data.decode())

    def _process_data(self, data):
        '''
        Upon parsing data, it will call 1 of 3 services offered by server:
            register, forward_msg, terminate 
        If data is not conforming to this, exception is raised & msg sent back to client
        '''

        # Parse data string
        pdata = parse_data(data)

        if pdata['cmd'] == "REG":
            self._register(name=pdata["name"], transport=self.transport)

        elif pdata['cmd'] == "SND":
            self._send_msg(target_name=pdata["dest"], msg=pdata["msg"])

        else:
            self.transport.write("Unknown CMD recieved! Please retry!".encode())
            raise Exception("Unknown CMD recieved from {}!".format(self.transport.get_extra_info("peername")))

    def _register(self, name, transport):
        '''
        Perform registration service.
        Save the client name and transport object'''

        global connections
        connections[name] = transport

        self.name = name
        self.transport = transport

        log.debug("Registered client [{0}] from [{1}]. Total registered clients = {2}!".format(name, transport.get_extra_info("peername"), len(connections)))

        return True

    def _send_msg(self, target_name, msg):
        '''
        Send/forward msg to target client
        '''
        global connections

        # Create message 
        data = render_msg(cmd="RCV", client=target_name, msg=msg)
        log.debug("Prepared message: [{}]".format(data))

        # Fetch target transport object
        target = connections.get(target_name)

        # Send data as bytestring. No need to yield!
        if target:
            target.write(data.encode())
            log.debug("Message sent [{0}] -> [{1}]".format(self.name, target_name))

        else:
            # No such target client found! Inform self
            errmsg = render_msg(cmd="ERR", msg="No such client!")
            self.transport.write(errmsg.encode())
            log.error("Error while sending msg from [{0}] -> [{1}]".format(self.name, target_name))

        return True

    def __del__(self):
        ''' 
        On Destructor 
        '''
        global _d_conn_counter

        msg = render_msg("BYE")
        self.transport.write(msg.encode())

        _d_conn_counter -= 1
        log.debug("Closing connection to [{0}]. Total left: {1}".format(self.name if self.name else self.transport.get_extra_info('peername'), _d_conn_counter))
        self.transport.close()
        


def start(host="0.0.0.0", port=8888):
    """
    Starts the Chat server and binds it to given host and port.
    """
    # Create event loop
    loop = asyncio.get_event_loop()

    # Create server object with Protocol Factory
    chatserver = loop.create_server(ChatServer, host, port)

    # Start server object to be closed
    server = loop.run_until_complete(chatserver)
    log.info('Started serving on {}'.format(server.sockets[0].getsockname()))

    # Start listen for concurrent connections
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        log.info("Server exiting!")
    finally:
        server.close()
        loop.close()


if __name__ == '__main__':
    start()