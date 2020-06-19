import logging
import datetime
from enum import Enum
from random import choice
from dataclasses import dataclass
from typing import Dict, Any, Type, Tuple, List, Callable

import pandas


class Columns(Enum):
    DATE = 'date'
    SENDER = 'sender'
    RECEIVER = 'receiver'
    QUOTE = 'quote'


@dataclass
class DataProxy:
    config: Dict[str, Any]

    @property
    def df(self):
        return pandas.read_csv(
            self.config['csv'],
            names=[col.value for col in Columns],
            parse_dates=[Columns.DATE.value]
    )

    def get_data_quote(self) -> Tuple[datetime.datetime, str]:
        df = self.df
        ntuple = choice(list(
            df[[Columns.DATE.value, Columns.QUOTE.value]]
              [df.quote.notna()].itertuples()
        ))
        return (
            getattr(ntuple, Columns.DATE.value),
            getattr(ntuple, Columns.QUOTE.value)
        )

    def get_data_metrics(
        self, fmt_user: Callable[[int], str]
    ) -> Dict[Columns, List[Tuple[str, int]]]:
        top = {}
        for utype in [Columns.SENDER, Columns.RECEIVER]:
            top[utype] = [
                (fmt_user(k), v)
                for k, v in self.df
                    .groupby(utype.value)
                    .size()
                    .sort_values(ascending=False)
                    .items()
                if k != -1  # there were no mentions
            ]
        return top

    def store(
            self, date: datetime.datetime, author: int,
            mentions: List[int], quote: str = ''
    ) -> None:
        data = zip(
            [date] * (len(mentions) or 1),
            [author] * (len(mentions) or 1),
            mentions or [-1],
            [quote] * (len(mentions) or 1)
        )
        df = pandas.DataFrame(data=data)
        logging.debug('Appending to %s:\n%r', self.config['csv'], df)
        df.to_csv(self.config['csv'], mode='a', header=False, index=False)
