import io
import random
import requests
import json
from typing import Tuple, Union
from functools import partial
from pkg_resources import resource_filename

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from discord import Embed, File
from discord.ext.commands import Cog, command

from bot.data import Columns
from bot.eloAOE import get_player_history, PlayerNotFound, generate_elo_plot, SOLO_GAME_MODE, TEAM_GAME_MODE


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

    @command(name='my-nice-messages', help='Retrieve messages that made people go like \'nice\'')
    async def my_nice_messages(self, ctx):
        embed = self._get_message_history(ctx.author.id, ctx.author.name, ctx.guild.id)
        await ctx.send(embed=embed)

    @command(name='nice-messages', help="<user: @mention> Retrieve messages that made people go like 'nice' by user")
    async def nice_messages(self, ctx):
        mentions = ctx.message.mentions
        if not mentions:
            await ctx.send("Please mention someone to get their nice messages.")
        elif len(mentions) > 1:
            await ctx.send("You can only check the messages of one person at a time.")
        else:
            target = mentions[0]
            embed = self._get_message_history(target.id, target.name, ctx.guild.id)
            await ctx.send(embed=embed)

    def _get_message_history(self, author_id: int, author_name: str, srv: int) -> Embed:
        messages = self.dp.get_all_nice_messages(srv=srv, author_id=author_id)
        embed = Embed(
            title=f'{author_name} nice messages',
            colour=0x00b2ff,
        )
        embed.add_field(
            name='These are the messages that had everyone going like \'nice\':',
            value='\n'.join(messages)
        )
        return embed

    @command(name='nice-fact', help='Cheers you up with a nice wholesome beautiful sweet sugary random fact ( ⋂‿⋂’).')
    async def nice_fact(self, ctx):
        fact = get_fact()
        if isinstance(fact, File):
            await ctx.send(ctx.author.mention, file=fact)
        else:
            await ctx.send(f'{ctx.author.mention} {fact}')

    @command(name='nice-elo', help='Returns elo niceness evolution')
    async def elo_solo_niceness(self, ctx, playerName, matches = 100):
        await ctx.trigger_typing()
        try:
            [plot, embed, axesData] = plot_elo_niceness(playerName, matches, SOLO_GAME_MODE)
        except PlayerNotFound:
            await ctx.send('Couldn\'t find any player called: ' + playerName)
            return
        ctx.send = partial(ctx.send, file=plot)
        await ctx.send(embed=embed)
        if (axesData['taunt']):
            ctx.send = partial(ctx.send, file=None)
            await ctx.send(axesData['taunt'])

    @command(name='nice-team-elo', help='Returns team elo niceness evolution')
    async def elo_shared_niceness(self, ctx, playerName, matches = 100):
        await ctx.trigger_typing()
        try:
            [plot, embed, axesData] = plot_elo_niceness(playerName, matches, TEAM_GAME_MODE)
        except PlayerNotFound:
            await ctx.send('Couldn\'t find any player called: ' + playerName)
            return
        ctx.send = partial(ctx.send, file=plot)
        await ctx.send(embed=embed)
        if (axesData['taunt']):
            ctx.send = partial(ctx.send, file=None)
            await ctx.send(axesData['taunt'])

def plot_elo_niceness(playerName, matches, gameMode = SOLO_GAME_MODE):
    axesData = get_player_history(playerName, matches, gameMode)
    [plot, embed] = generate_elo_plot(axesData)
    return [plot, embed, axesData]


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


def get_fact() -> Union[str, File]:
    if random.random() < 0.1:
        with open(
            file=resource_filename(
                'bot', 'resources/nicethumbsup.gif'
            ),
            mode='rb'
        ) as f:
            picture = File(f)
        return picture
    with open(
        file=resource_filename('bot', 'resources/facts.txt'),
        mode='r'
    ) as f:
        content = [block.strip() for block in f.read().split('---')]
    return random.choice(content)

