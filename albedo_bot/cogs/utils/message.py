from discord.ext.commands.context import Context


def wrap_message(message: str, wrapper: str = ""):
    """_summary_

    Args:
        message (str): _description_
    """

    max_message_length = 2000 - len(wrapper)
    message_list = []
    start_message = 0
    while start_message < len(message):
        if wrapper != "":
            new_message = wrapper.format(
                message[start_message:start_message+max_message_length])
        else:
            new_message = f"{message[start_message:start_message+max_message_length]}"
        message_list.append(new_message)
        start_message += len(new_message)
    return message_list


async def send_message(ctx: Context, message: str, css=True, wrapper: str = ""):
    """_summary_

    Args:
        ctx (Context): _description_
        message (_type_): _description_
    """
    css_wrapper = "```css\n{}\n```"
    if css:
        message_list = wrap_message(message, css_wrapper)
    else:
        message_list = wrap_message(message, wrapper)
    for message_instance in message_list:
        await ctx.send(message_instance)
