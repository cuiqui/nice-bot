import logging
import logging.config
from typing import Mapping
from dataclasses import dataclass, field

from discord.ext.commands import Bot

from bot.data import DataProxy
from bot.cogs.commands import Commands
from bot.cogs.listeners import Listeners


@dataclass
class Bootstrap:
    config: Mapping
    bot: Bot = field(init=False)
    dp: DataProxy = field(init=False)

    def __post_init__(self):
        logging.config.dictConfig(self.config['logging'])
        self.configure_dataproxy()
        self.configure_bot()

    def configure_dataproxy(self):
        self.dp = DataProxy(config=self.config['bot'])

    def configure_bot(self):
        bot = Bot(command_prefix='!', help_attrs={'name': 'nice-help'})
        cogs = [
            Listeners(bot, self.dp, self.config['bot']),
            Commands(bot, self.dp)
        ]
        for cog in cogs:
            bot.add_cog(cog)
        self.bot = bot
