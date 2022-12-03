import logging
import os

LOG_FILE = 'file-server_log.log'
path = os.getcwd() + '/' + 'logs'
try:
    os.mkdir(path)
except FileExistsError:
    pass
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(
    filename=path + '/' + LOG_FILE,
    mode='w',
    encoding='utf-8',
    delay=True
)
formatter: logging.Formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
)
ch.setFormatter(formatter)
logger.addHandler(ch)
