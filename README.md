asio_chatserver
===============

A simple chatserver application using asyncio.


This project was done as part of a challenge to test the capabilities of Python vs Go.
I accepted the challenge to write the chatserver in Python3.4 using asyncio.

For the sake of making it a relatively realistic test, a rudimentary protocol was introduced.

**CLIENT to SERVER**
- To register a client with server: 
  - REG [4 ascii chars for len of data including whitepace] [client name]  \(eg: REG 0007 TEST01\)
- To send a message to a client: 
  - SND [4 ascii chars for message len including whitespace] [target client name] [message]  \(eg: SND 0017 TEST01 Heyyyooo!\)

**SERVER to CLIENT**
- To forward message from one client to another:
  - RCV [message length] [sender name] [word count] [message]  (eg: RCV 0022 TEST02 0001 Heyyyooo!)
- To cleanly disconnect with client:
  - BYE 0000


### Status so far
----
**NOTE**: The server application code at this point is incomplete and unoptimized.

Since this is using asyncio, it is limited by selectors implementation. This means, in Linux, asyncio uses epoll() to setup connections. In which case it can setup about 1024 concurrent connections (by default) before it runs out of file descriptors. So remember to use
```bash
ulimit -n 35565
```
to increase the number of allocated file descriptors for that session. Alternatively, u can change the FD_SETSIZE for a more permanent fix.

In windows, asyncio uses select(), so the number of connection is even less. I'm not sure how to increase this limit. Not yet tested on Mac OSX.

A test application was prepared for this in C, using boost-asio library. 
A 'burst' of 10000 parallel connections were made to the server application - It was able to register upto 8500 connections (as per logs), before the server app seemed to drop other connections. Not sure if this is a python problem, or kernel level problem.
However, serially, it has been observed that the app was able to connect and serve all 35565 connections. This is quite impressive, considering this is a single-threaded app (albeit wonderfully event-driven).

I'm seriously loving asyncio!! 
