from discord.ext.commands.context import Context

from albedo_bot.commands.helpers.checklist import (
    checklist_command, show_checklist, _list_checklist)


@checklist_command.command(name="show")
async def hero_list(ctx: Context, checklist_name: str):
    """_summary_

    Args:
        ctx (Context): _description_
        checklist_name (str): _description_
    """

    await show_checklist(ctx, checklist_name)


@checklist_command.command(name="list")
async def list_checklist(ctx: Context):
    """[summary]

    Args:
        ctx (Context): invocation context containing information on how
            a discord event/command was invoked
        name (str): [description]
    """

    checklist_result = await _list_checklist()
    joined_result = "\n".join([str(checklist_instance)
                              for checklist_instance in checklist_result])
    await ctx.send(f"```\n{joined_result}\n```")
