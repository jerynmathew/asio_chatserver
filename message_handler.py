import re


pattern = "(?P<cmd>REG|SND|RCV|BYE|ERR)\s?(?P<len>\d{4})\s?(?P<msg>.*)"
rx_obj  = re.compile(pattern)


def parse_data(data):
    ''' Parse data string'''
    # FORMATS: 
    # REG <ascii 4 bytes>[ <name>]
    # SND <ascii 4 bytes>[ <name of recipient>][ <msg>]
    # RCV <ascii 4 bytes>[ <name of sender>][ <ascii 4 bytes word count>][ <msg>]
    # BYE 0000
    global rx_obj

    match = rx_obj.match(data)
    if match is None:
        raise Exception("Non-compliant data format! Please resend data!")

    # Prepare data to send back
    pdata = {"cmd": match.group("cmd"),
             "len": int(match.group("len"))}

    if pdata["cmd"] == "REG":
        pdata["name"] = match.group("msg").split(" ", 1)[0]

    elif pdata["cmd"] == "SND":
        pdata["dest"], pdata["msg"] = match.group("msg").split(" ", 1)

    elif pdata["cmd"] == "RCV":
        # XXX: Potential overflow issue here, if u do not ensure wordcount limit on msg
        pdata["src"], _, pdata["msg"] = match.group("msg").split(" ", 2)

    elif pdata["cmd"] == "ERR":
        pdata["src"] = "SERVER"
        pdata["msg"] = match.group("msg")

    return pdata


def render_msg(cmd="RCV", client=None, msg=None):
    '''
    Create the message to send/forward to client.
    '''
    reg_template = "REG {len:0>4} {client}"
    snd_template = "SND {len:0>4} {client} {msg}"
    rcv_template = "RCV {len:0>4} {client} {wc:0>4} {msg}"
    err_template = "ERR {len:0>4} {msg}"
    bye_template = "BYE 0000"

    mstring = None

    if cmd == "REG":
        mlen = len(client) + 1  # Whitespace

        mstring = reg_template.format(len=mlen, client=client)

    elif cmd == "SND":
        mlen = len(client) + \
               len(msg) + \
               2   # Whitespace

        mstring = snd_template.format(len=mlen, client=client, msg=msg)

    elif cmd == "RCV":
        mlen = len(client) + \
               len(msg) + \
               4 + 3    # 4 for wc; 3 for Whitespace

        wc = len(msg.split(" "))

        mstring = rcv_template.format(len=mlen, client=client, wc=wc, msg=msg)

    elif cmd == "ERR":
        mlen = len(msg) + 1

        mstring = err_template.format(len=mlen, msg=msg)

    elif cmd == "BYE":
        mstring = bye_template

    return mstring