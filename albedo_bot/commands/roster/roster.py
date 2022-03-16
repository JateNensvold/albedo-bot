import json
from discord.ext.commands.context import Context

from albedo_bot.commands.helpers.converter import HeroConverter
from albedo_bot.commands.helpers.roster import (
    roster_command, fetch_roster, _add_hero)
import zmq
import zmq.asyncio
import image_processing.globals as IP_GV
from image_processing.processing_client import check_socket, process_image


@roster_command.command(name="show", aliases=["list"])
async def show(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    heroes_result = fetch_roster(ctx.author.id)
    await ctx.send(heroes_result)


@roster_command.command(name="add", aliases=["update"])
async def add_hero(ctx: Context, hero: HeroConverter,
                   ascension: str, signature_item: int, furniture: int,
                   engraving: int):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """
    await _add_hero(ctx, ctx.author, hero, ascension, signature_item, furniture,
                    engraving)


@roster_command.command(name="upload")
async def upload(ctx: Context):
    """_summary_

    Args:
        ctx (Context): _description_
    """

    context = zmq.Context()
    socket = context.socket(zmq.DEALER)  # pylint: disable=no-member

    for attachment in ctx.message.attachments:
        socket.connect("tcp://localhost:5555")
        # message = " ".join(sys.argv[1:])
        print(f"Message: {str(attachment)}")
        socket.send_string(str(attachment))
        received = socket.recv()
        # print(received)
        json_dict = json.loads(received)
        # print(json_dict)
        import pprint

        dict_message = pprint.pformat(json_dict, width=200)
        start_message = 0
        print(dict_message)
        while start_message < len(dict_message):
            await ctx.send(f"```\n{dict_message[start_message:start_message+1991]}\n```")
            start_message += 1991


        # print(str(attachment))
        # socket.connect("tcp://localhost:5555")
        # print("Connected")
        # socket.send_string(str(attachment))
        # print("Sent")
        # socket_message = await socket.recv()
        # json_dict = json.loads(socket_message)

        # await ctx.send(str(attachment))

        # await ctx.send(str(json_dict))
    #     attachment_list.append(str(attachment))
    # await ctx.send("\n".join(attachment_list))
