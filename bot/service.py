import sys
import signal
import logging
import logging.config

import confight
from pid import PidFile, PidFileError

from bot.bootstrap import Bootstrap


class Service:
    def start(self) -> None:
        config = confight.load_app('nice-bot', extension='toml')
        signal.signal(signal.SIGINT, self.shutdown)
        bootstrap = Bootstrap(config)
        bot, dp = bootstrap.bot, bootstrap.dp
        logging.info('Starting nice-bot')
        logging.info('Database shape: %r', dp.df.shape)
        bot.run(config['bot']['token'])

    def shutdown(self, _signal, _stack) -> None:
        logging.info('SIGINT received')
        sys.exit(1)


def main() -> None:
    try:
        with PidFile(
            'nice-bot',
            piddir='/var/lib/nice-bot'
        ):
            Service().start()
    except PidFileError:
        logging.error('Nice-bot is already running')
        raise
