from discord.ext.commands.context import Context


def wrap_message(message: str, wrapper: str = "", header: str = ""):
    """_summary_

    Args:
        message (str): _description_
    """

    max_message_length = 2000 - len(wrapper) - len(header)
    message_list = []
    message_itr_index = 0
    while message_itr_index < len(message):

        new_message = message[message_itr_index:message_itr_index +
                              max_message_length]
        newline_index = new_message.rfind("\n")

        if newline_index not in [0, -1] and (message_itr_index + len(new_message)) < len(message):
            new_message = message[message_itr_index:message_itr_index+newline_index+1]

        if wrapper != "":
            new_message = wrapper.format(
                new_message)
        message_list.append(f"{header}{new_message}")
        message_itr_index += len(new_message)
    return message_list


async def send_message(ctx: Context, message: str, header: str = "",
                       css: bool = True, wrapper: str = ""):
    """_summary_

    Args:
        ctx (Context): _description_
        message (_type_): _description_
    """
    css_wrapper = "```css\n{}\n```"

    if header == "":
        header = f"{ctx.author.mention}\n"

    if css:
        wrapper = css_wrapper
    message_list = wrap_message(message, wrapper, header)
    for message_instance in message_list:
        await ctx.send(message_instance)
