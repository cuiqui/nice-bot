import logging
import datetime
from enum import Enum
from random import choice
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List, Callable, Union

import pandas


class Columns(Enum):
    SERVER = 'server'
    DATE = 'date'
    SENDER = 'sender'
    RECEIVER = 'receiver'
    QUOTE = 'quote'


@dataclass
class DataProxy:
    config: Dict[str, Any]

    @property
    def df(self):
        try:
            return pandas.read_csv(
                self.config['csv'],
                names=[col.value for col in Columns],
                parse_dates=[Columns.DATE.value]
            )
        except FileNotFoundError:
            return pandas.DataFrame(columns=[col.value for col in Columns])

    def get_data_quote(
            self, srv: int
    ) -> Union[Tuple[datetime.datetime, str], Tuple[None, None]]:
        df = self.df
        ntuple = list(
            df[[Columns.DATE.value, Columns.QUOTE.value]]
              [((df[Columns.SERVER.value] == srv) &
                (df[Columns.QUOTE.value].notna()))].itertuples()
        )
        if ntuple:
            quote = choice(ntuple)
            return (
                getattr(quote, Columns.DATE.value),
                getattr(quote, Columns.QUOTE.value)
            )
        return None, None

    def get_data_metrics(
        self, srv: int, fmt_user: Callable[[int], str]
    ) -> Dict[Columns, List[Tuple[str, int]]]:
        df = self.df
        top = {}
        for utype in [Columns.SENDER, Columns.RECEIVER]:
            top[utype] = [
                (fmt_user(k), v)
                for k, v in df[df[Columns.SERVER.value] == srv]
                    .groupby(utype.value)
                    .size()
                    .sort_values(ascending=False)
                    .items()
                if k != -1  # there were no mentions
            ]
        return top

    def store(
            self, srv: int, date: datetime.datetime,
            author: int, mentions: List[int], quote: str = ''
    ) -> None:
        data = zip(
            [srv] * (len(mentions) or 1),
            [date] * (len(mentions) or 1),
            [author] * (len(mentions) or 1),
            mentions or [-1],
            [quote] * (len(mentions) or 1)
        )
        df = pandas.DataFrame(data=data)
        logging.debug('Appending to %s:\n%r', self.config['csv'], df)
        df.to_csv(self.config['csv'], mode='a', header=False, index=False)

    def process_complaint(self, complaint: str) -> None:
        # made you look, dumbass.
        del complaint

    def get_all_nice_messages(self, srv: int, author_id: int):
        df = self.df
        quotes = df[(df[Columns.RECEIVER.value] == author_id) &
                    (df[Columns.SERVER.value] == srv)]
        return quotes[Columns.QUOTE.value].to_list()
