from discord.ext.commands.context import Context


def wrap_css(message: str):
    """_summary_

    Args:
        message (str): _description_
    """
    css_length = 11
    message_list = []
    start_message = 0
    while start_message < len(message):
        message_list.append(
            f"```css\n{message[start_message:start_message+2000 - css_length]}\n```")
        start_message += 2000 - css_length
    # await ctx.send(message)
    return message_list


async def send_css_message(ctx: Context, message: str):
    """_summary_

    Args:
        ctx (Context): _description_
        message (_type_): _description_
    """
    message_list = wrap_css(message)
    for message_instance in message_list:
        await ctx.send(message_instance)
