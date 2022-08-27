"""Function that routes symbols to the correct API provider.
"""

import datetime
import logging
import random
import re
from logging import critical, debug, error, info, warning

import pandas as pd
import schedule
from cachetools import TTLCache, cached

from bybit_Crypto import BybitCrypto
from Symbol import Coin, Symbol


class Router:
    CRYPTO_REGEX = r"([a-zA-Z]{2,20})"
    FREQ_REGEX = r"([\d]{1,2}[\w]{1})"

    def __init__(self):
        self.crypto = BybitCrypto()

    def find_symbols(self, text: str) -> list[Symbol]:
        """Finds stock tickers starting with a dollar sign, and cryptocurrencies with two dollar signs
        in a blob of text and returns them in a list.

        Parameters
        ----------
        text : str
            Blob of text.

        Returns
        -------
        list[Symbol]
            List of stock symbols as Symbol objects
        """
        schedule.run_pending()

        symbols = []

        coins = set(re.findall(self.CRYPTO_REGEX, text))
        for coin in coins:
            sym = self.crypto.symbol_list[
                self.crypto.symbol_list["baseCurrency"].str.fullmatch(
                    coin.upper(), case=False
                )
            ]
            if ~sym.empty:
                symbols.append(Coin(sym))
            else:
                info(f"{coin} is not in list of coins")
        if symbols:
            info(symbols)
            return symbols

    def find_chart_interval(self, text: str) -> str:
        """


        Parameters
        ----------
        text : str
            Blob of text.

        Returns
        -------
        list[Symbol]
            List of stock symbols as Symbol objects

        """
        frequency_list = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w', '1M']

        frequency = max(set(re.findall(self.FREQ_REGEX, text)))

        ######################

        if frequency_list.count(frequency) > 0:
            return frequency
        else:
            info(f"{frequency} provided does not match an expected timeframe.")

    def status(self, bot_resp) -> str:
        """Checks for any issues with APIs.

        Returns
        -------
        str
            Human readable text on status of the bot and relevant APIs
        """

        stats = f"""
        Bot Status:
        {bot_resp}

        Cryptocurrency Data:
        {self.crypto.status()}
        """

        warning(stats)

        return stats

    def chart_reply(self, symbol: Symbol, freq: str) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        freq: str
            Chart frequency

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available.
                Otherwise returns empty pd.DataFrame.
        """

        if isinstance(symbol, Coin):
            return self.crypto.chart_reply(symbol, freq)
        else:
            debug(f"{symbol} is not a Stock or Coin")
            return pd.DataFrame()

    def stat_reply(self, symbols: list[Symbol]) -> list[str]:
        """Gets key statistics for each symbol in the list

        Parameters
        ----------
        symbols : list[str]
            List of stock symbols

        Returns
        -------
        Dict[str, str]
            Each symbol passed in is a key with its value being a human readable
                formatted string of the symbols statistics.
        """
        replies = []

        for symbol in symbols:

            if isinstance(symbol, Coin):
                replies.append(self.crypto.stat_reply(symbol))
            else:
                debug(f"{symbol} is not a Stock or Coin")

        return replies
