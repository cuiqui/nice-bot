import re
import io
import logging
from typing import Dict, List, Tuple
from functools import partial

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from discord import Embed, File, Message
from discord.ext.commands import Bot, Command

from bot.data import Columns


NICE_REGEX = re.compile('(?<!\S)n+i+c+e+(?!\S)', re.IGNORECASE)


class NiceBot(Bot):

    def __init__(self, config: Dict, dp: 'DataProxy'):
        super().__init__(command_prefix='!')
        self.config = config
        self.dp = dp

    def start(self):
        self._register_actions()
        self.run(self.config['bot']['token'])

    def _register_actions(self):
        commands = [
            Command(
                self.metrics, name='nice-metrics', help='Display niceness'
            ),
            Command(
                self.quote, name='nice-quote', help='Retrieve random quote'
            )
        ]
        for command in commands:
            self.add_command(command)
        self.add_listener(self.on_ready, name='on_ready')
        self.add_listener(self.on_message, name='on_message')

    async def on_ready(self):
        logging.info('Logged in as {0.user}'.format(self))

    async def on_message(self, msg):
        if msg.author == self.user:
            return

        content, quote = process_message(msg)

        if NICE_REGEX.search(content):
            row = {
                'date': msg.created_at,
                'author': msg.author.id,
                'mentions': [mem.id for mem in msg.mentions],
                'quote': quote
            }
            logging.info('Storing entry: %r', row)
            self.dp.store(**row)
            await msg.channel.send('𝓷𝓲𝓬𝓮 ☜(ﾟヮﾟ☜)')
        await self.process_commands(msg)

    async def quote(self, ctx):
        await ctx.send(f'Someone said:\n{self.dp.get_data_quote()}')

    async def metrics(self, ctx):
        embed = Embed(
            title='Niceness leaderboard',
            colour=0x00b2ff,
        )
        data = self.dp.get_data_metrics(
            lambda uid: self.get_user(uid).name
        )
        for k, v in data.items():
            board = generate_board(v)
            embed.add_field(
                name=k.value.title(),
                value=board if board else 'N/A',
                inline=False
            )
        if data.get(Columns.RECEIVER):
            plot = File(
                fp=generate_plot(data[Columns.RECEIVER]),
                filename='graph.png'
            )
            embed.set_image(url=f'attachment://graph.png')
            ctx.send = partial(ctx.send, file=plot)
        await ctx.send(embed=embed)


def process_message(msg: Message) -> Tuple[str, str]:
    quote = ''
    content = ''
    for line in msg.clean_content.split('\n'):
        if line.startswith('>'):
            quote += line[2:]
        else:
            content += line
    return content, quote


def generate_board(data: Tuple[str, int]) -> str:
    board = ''
    for i, score in enumerate(data, start=1):
        board += f'**{i}. {score[0]}:** {score[1]}\n'
    return board


def generate_plot(data: Tuple[str, int]) -> io.BytesIO:
    user, score = zip(*data)
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    ax.barh(
        y=user,
        width=score,
        align='center',
        color='#47a0ff'
    )
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.invert_yaxis()
    buf = io.BytesIO()
    fig.savefig(buf, transparent=True, format='png')
    buf.seek(0)
    return buf
