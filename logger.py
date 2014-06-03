import logging


console = None

def setup_logging(name=None):
    # global log
    global console

    log = logging.getLogger(name if name else __name__)
    log.setLevel(logging.DEBUG)

    # Set Handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # console = get_colored_streamhandler(console)

    # Set Formatter
    formatter = logging.Formatter("%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s %(message)s")
    console.setFormatter(formatter)

    # Add Handler to logger
    log.addHandler(console)

    log.debug("Setup logging!")

    return log