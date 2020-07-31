import io
import random
from typing import Tuple, Union
from functools import partial
from pkg_resources import resource_filename

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from discord import Embed, File
from discord.ext.commands import Cog, command

from bot.data import Columns


class Commands(Cog):
    def __init__(self, bot: 'NiceBot', dp: 'DataProxy'):
        self.bot = bot
        self.dp = dp

    @command(name='nice-wisdom', help='Retrieve random nice quote')
    async def quote(self, ctx):
        date, quote = self.dp.get_data_quote(srv=ctx.guild.id)
        d_fmt = 'Heard on a %c'
        embed = Embed(
            title='Nice wisdom',
            colour=0x00b2ff,
        )
        embed.add_field(
            name=f'{date.strftime(d_fmt) if date else "N/A"}:',
            value=quote or "N/A"
        )
        await ctx.send(embed=embed)

    @command(name='nice-metrics', help='Retrieve nice leaderboard')
    async def metrics(self, ctx):
        embed = Embed(
            title='Niceness leaderboard',
            colour=0x00b2ff,
        )
        data = self.dp.get_data_metrics(
            srv=ctx.guild.id,
            fmt_user=lambda uid: self.bot.get_user(uid).name
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
        await ctx.send(ctx.author.mention, embed=embed)

    @command(name='bad-bot', help='<feedback: str> Help us improve!')
    async def complaint(self, ctx, content: str):
        self.dp.process_complaint(content)
        comeback = get_comeback()
        if isinstance(comeback, File):
            await ctx.send(ctx.author.mention, file=comeback)
        else:
            await ctx.send(f'{ctx.author.mention} {comeback}')

    @command(name='my-nice-messages', help='Retrieve the messages that made people go like \'nice\'')
    async def my_nice_messages(self, ctx):
        author_id = ctx.author.id
        srv = ctx.guild.id
        messages = self.dp.get_all_nice_messages(srv=srv, author_id=author_id)
        embed = Embed(
            title='Your nice messages',
            colour=0x00b2ff,
        )
        embed.add_field(
            name='These are the messages that had everyone going like \'nice\':',
            value='\n'.join(messages)
        )
        await ctx.send(embed=embed)

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


def get_comeback() -> Union[str, File]:
    if random.random() < 0.1:
        with open(
            file=resource_filename(
                'bot', 'resources/invisible_typewriter.gif'
            ),
            mode='rb'
        ) as f:
            picture = File(f)
        return picture
    with open(
        file=resource_filename('bot', 'resources/comebacks.txt'),
        mode='r'
    ) as f:
        content = [block.strip() for block in f.read().split('---')]
    return random.choice(content)
