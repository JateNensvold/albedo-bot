import logging
from logging.handlers import RotatingFileHandler

from albedo_bot.albedo_main import RemoveNoise

class LoggingManager:
    def __init__(self):
        pass

    def setup_logging():
        """
        Setup discord logging
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
                '[{asctime}] [{levelname:<7}] {name}: {message}',
                date_format, style='{')
            handler.setFormatter(log_format)
            log.addHandler(handler)

            yield
        finally:
            # __exit__
            handlers = log.handlers[:]
            for handler in handlers:
                handler.close()
                log.removeHandler(handler)