

import argparse
import asyncio
import contextlib
import logging
from logging.handlers import RotatingFileHandler
from typing import NamedTuple


from albedo_bot.bot import AlbedoBot
import albedo_bot.config as config


class RemoveNoise(logging.Filter):
    """_summary_

    Args:
        logging (_type_): _description_
    """

    def __init__(self):
        super().__init__(name='discord.state')

    def filter(self, record):
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        return True


@contextlib.contextmanager
def setup_logging():
    """_summary_
    """
    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename='albedo_bot.log',
                                      encoding='utf-8', mode='w',
                                      maxBytes=max_bytes, backupCount=5)
        date_format = '%Y-%m-%d %H:%M:%S'
        log_format = logging.Formatter(
            '[{asctime}] [{levelname:<7}] {name}: {message}', date_format, style='{')
        handler.setFormatter(log_format)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)


def run_bot():
    """_summary_
    """

    bot = AlbedoBot()
    bot.run()


class LaunchChoices(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """
    run: str = "run"
    init: str = "init"
    drop: str = "drop"
    reset: str = "reset"


def main():
    """Launches the bot."""

    launch_choices = LaunchChoices()

    parser = argparse.ArgumentParser(
        description='AFK arena Roster management Bot')

    parser.add_argument("mode", type=str, nargs="?", default=launch_choices.run,
                        choices=launch_choices,
                        help="Mode to launch Albedo Bot with")
    parser.add_argument("-v", "--verbose", help="Increase verbosity of output"
                        "from discord commands", action='count', default=0)

    args = parser.parse_args()

    config.VERBOSE = args.verbose
    loop = asyncio.get_event_loop()
    database = config.database

    if args.mode == launch_choices.run:
        with setup_logging():
            run_bot()
    elif args.mode == launch_choices.init:
        database.select_database("postgres")
        loop.run_until_complete(database.init_database(
            config.database_name, raise_error=False))
    elif args.mode == launch_choices.drop:
        loop.run_until_complete(database.drop_database(config.database_name))
    elif args.mode == launch_choices.reset:
        database.select_database(config.database_name)
        loop.run_until_complete(database.reset_database())

if __name__ == '__main__':
    main()
