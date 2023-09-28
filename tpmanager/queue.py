import time
from enum import Enum
from mcdreforged.api.all import *

from . import config

tp_queue = {}
back_queue = {}

server: PluginServerInterface = None


class Result(Enum):
    NONE = 0
    HAS = 1
    TIMEOUT = 2


def find(source: str, target: str):
    id = source + ':' + target
    if id not in tp_queue:
        return Result.NONE
    if time.time() - tp_queue[id] >= config.tp_timeout:
        tp_queue.pop(id)
        return Result.TIMEOUT
    return Result.HAS


def send(source: str, target: str):
    id = source + ':' + target
    tp_queue[id] = time.time()


def handle(source: str, target: str):
    id = source + ':' + target
    if id in tp_queue:
        tp_queue.pop(id)


def tick():
    if server is None:
        return
    items = list(tp_queue.items())
    for id,lastTime in items:
        if time.time() - lastTime>= config.tp_timeout:
            tp_queue.pop(id)
            args = id.split(':')
            source, target = args
            server.tell(source, f"发送给{target}的请求已经过期")
            server.tell(target, f"{source}给你的请求已经过期")
