from mcdreforged.api.all import *
from minecraft_data_api import Coordinate, get_player_coordinate, get_player_info, get_server_player_list
import time

from tpmanager import config, queue


def player_online_check(source: PlayerCommandSource, target: str):
    if not source.is_player:
        source.reply('你必须是玩家.')
        return True

    player_list = get_server_player_list(timeout=config.query_timeout)[2]
    player_list = () if player_list is None else player_list
    if target not in player_list:
        source.reply(RText('玩家不在线', RColor.green))
        return True
    return False


@new_thread("Teleport Thread")
def tpa(source: PlayerCommandSource, args: dict):
    target = args['player']
    if player_online_check(source, target):
        return
    name = source.get_info().player
    queue.send(name, target)
    source.reply(RText(f"发送请求给 {target}", RColor.green))
    source.get_server().tell(target, RText(
        f"{name} 请求传送到你这里，你有{config.tp_timeout}秒的时间接受\n!!tpyes {name}\n!!tpno {name}", RColor.green))


@new_thread("Teleport Thread")
def tpto(source: PlayerCommandSource, request_source: str, coordinate: Coordinate, dimension: str):
    server = source.get_server()
    server.tell(request_source, RText(f"{source.player} 已经同意请求", RColor.green))
    queue.handle(request_source, source.get_info().player)
    for i in range(3):
        time.sleep(1)
        server.tell(request_source, RText(f"传送倒计时 {3 - i}", RColor.green))
    source.get_server().execute(f"/execute in {dimension} run "
                                f"tp {request_source} {coordinate.x} {coordinate.y} {coordinate.z}")
    queue.back_queue[request_source] = {
        "dimension": dimension,
        "coordinate": f"{coordinate.x} {coordinate.y} {coordinate.z}"
    }
    server.tell(request_source, RText('已经传送', RColor.green))
    server.tell(request_source, RText('!!back 可以回到上个位置', RColor.green))


@new_thread("Teleport Thread")
def back(source: PlayerCommandSource):
    if source.player not in queue.back_queue:
        source.reply(RText("你没有传送过", RColor.red))
    else:
        source.reply(RText(f"正在传送", RColor.green))
        location = queue.back_queue.pop(source.player)
        for i in range(3):
            time.sleep(1)
            source.reply(RText(f"传送倒计时 {3 - i}", RColor.green))
        print(location)
        source.get_server().execute(f"/execute in {location['dimension']} run "
                                    f"tp {source.player} {location['coordinate']}")


def get_dimension(source: str):
    return get_player_info(source, 'Dimension', timeout=config.query_timeout)


@new_thread("Teleport Thread")
def tpacccept(source: PlayerCommandSource, args: dict):
    request_source: str = args['player']
    if player_online_check(source, request_source):
        return

    rst = queue.find(request_source, source.get_info().player)
    if rst == queue.Result.HAS:
        coordinate = get_player_coordinate(source.player, timeout=config.query_timeout)
        dimension = get_dimension(source.player)
        tpto(source, request_source, coordinate, dimension)
        source.reply(RText('你同意了对方的请求', RColor.green))
    elif rst == queue.Result.TIMEOUT:
        source.reply(RText("请求已过期", RColor.green))
    else:
        source.reply(RText("没有对方的请求", RColor.green))

    queue.handle(request_source, source.get_info().player)


@new_thread("Teleport Thread")
def tpdeny(source: PlayerCommandSource, args: dict):
    request_source = args['player']
    if player_online_check(source, request_source):
        return

    rst = queue.find(request_source, source.get_info().player)
    if rst == queue.Result.HAS:
        server = source.get_server()
        server.tell(request_source, f"{source.player} 已经拒绝请求")
        source.reply(RText("你已经拒绝请求", RColor.green))
    elif rst == queue.Result.TIMEOUT:
        source.reply(RText("请求已过期", RColor.green))
    else:
        source.reply(RText("没有对方的请求", RColor.green))

    queue.handle(request_source.source.get_info().player)
