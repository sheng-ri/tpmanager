from mcdreforged.api.all import *
import time

from tpmanager import queue, commands


def register_command(server: PluginServerInterface):
    builder = SimpleCommandBuilder()

    builder.command('!!tpa <player>', commands.tpa)

    builder.command('!!tpyes <player>', commands.tpacccept)
    builder.command('!!tpayes <player>', commands.tpacccept)

    builder.command('!!tpno <player>', commands.tpdeny)
    builder.command('!!tpano <player>', commands.tpdeny)

    builder.command("!!back", commands.back)

    builder.arg('player', Text)
    builder.register(server)


@new_thread('TpManager Request Maintain')
def maintain_request(server: PluginServerInterface):
    queue.server = server
    while server.is_server_running():
        time.sleep(5)
        queue.tick()


def on_load(server: PluginServerInterface, prev_modules):
    register_command(server)
    maintain_request(server)
