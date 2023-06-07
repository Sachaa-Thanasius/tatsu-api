import logging


class CustomColourFormatter(logging.Formatter):
    """Custom logging formatter for testing purposes. Copied from discord.py.

    References
    ----------
    https://github.com/Rapptz/discord.py/blob/master/discord/utils.py#L1262
    """

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record: logging.LogRecord) -> str:
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red.
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer.
        record.exc_text = None
        return output


def setup_logging():
    # Create loggers.
    logging.getLogger("tatsu").setLevel(logging.DEBUG)
    root_logger = logging.getLogger()

    # Add formatter, handler to root logger.
    handler = logging.StreamHandler()
    # dt_fmt = "%Y-%m-%d %H:%M:%S"
    # fmt = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    fmt = CustomColourFormatter()
    handler.setFormatter(fmt)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
