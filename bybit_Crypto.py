"""Class with functions for running the bot with ByBit API.
"""

import logging
from datetime import datetime
from logging import critical, debug, error, info, warning
from typing import List, Optional, Tuple

import pandas as pd
import requests as r
import schedule
import os
from pybit import spot
import datetime as dt

from Symbol import Coin

logging.basicConfig(filename="pybit.log", level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s")

BYBIT_KEY = os.environ["BYBIT_KEY"]
BYBIT_SECRET = os.environ["BYBIT_SECRET"]


class BybitCrypto:
    """
    Functions for finding crypto info
    """

    vs_currency = "USDT"

    session = spot.HTTP(
        endpoint='https://api.bybit.com',
        api_key=BYBIT_KEY,
        api_secret=BYBIT_SECRET
    )
    # simple/supported_vs_currencies for list of options

    searched_symbols = {}
    trending_cache = None

    def __init__(self) -> None:
        """Creates a Symbol Object

        Parameters
        ----------
        IEX_TOKEN : str
            IEX Token
        """
        self.get_symbol_list()
        schedule.every().day.do(self.get_symbol_list)

    def symbol_id(self, symbol) -> str:
        """

        """
        try:
            return self.symbol_list[self.symbol_list["baseCurrency"] == symbol]["baseCurrency"].values[
                0
            ]
        except KeyError:
            return ""

    def get_symbol_list(
        self, return_df=False
    ) -> Optional[Tuple[pd.DataFrame, datetime]]:
        """

        """

        resp = self.session.query_symbol()

        df = pd.DataFrame(resp['result'])

        df = df[df['quoteCurrency'] == self.vs_currency]

        df = df[['baseCurrency']]

        self.symbol_list = df

        if return_df:
            return df, datetime.now()

    def status(self) -> str:
        """Checks CoinGecko /ping endpoint for API issues.

        Returns
        -------
        str
            Human readable text on status of CoinGecko API
        """
        url = "https://api.bybit.com/spot/v1/time"

        status = r.get(url, timeout=5)

        try:
            status.raise_for_status()
            return f"ByBit API responded that it was OK with a {status.status_code} in {status.elapsed.total_seconds()} Seconds."
        except:
            return f"ByBit API returned an error code {status.status_code} in {status.elapsed.total_seconds()} Seconds."

    def get_one_hour_change(self, symbol: Coin, current_price: float) -> float:
        """Returns 1hr change price for specific token.

        Parameters
        ----------
        symbol : str
            Token symbol.

        current_price : float
            Current price.

        Returns
        -------
        float
            Returns a float with 1hr change data for requested symbol.
        """
        df = self.chart_reply(symbol=symbol, frequency='1h')

        df.sort_index(ascending=False, inplace=True)

        past_hr_close = float(df['Close'][0])

        return (float(current_price) / float(past_hr_close) - 1) * 100

    def chart_reply(self, symbol: Coin, frequency: str) -> pd.DataFrame:
        """Returns price data for a symbol of the past month up until the previous trading days close.
        Also caches multiple requests made in the same day.

        Parameters
        ----------
        symbol : str
            Stock symbol.

        frequency : str
            Frequency of candles.

        Returns
        -------
        pd.DataFrame
            Returns a timeseries dataframe with high, low, and volume data if its available.
            Otherwise returns empty pd.DataFrame.
        """
        if data := self.session.query_kline(
                symbol=symbol.symbol + self.vs_currency, interval=frequency
        )['result']:

            columns = ['startTime', 'open', 'high', 'low', 'close', 'volume', 'endTime', 'quoteAssetVolume', 'trades',
                       'takerBaseVolume', 'takerQuoteVolume']

            df = pd.DataFrame(data, columns=columns)

            df['startTime'] = df['startTime'].apply(lambda x: dt.datetime.utcfromtimestamp(x / 1000))

            df = df[['startTime', 'open', 'high', 'low', 'close']]

            df.rename(columns={'startTime': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'},
                      inplace=True)

            df['Date'] = pd.to_datetime(df['Date'], unit='ms')

            df = df.set_index('Date')

            df = df.astype(float)

            df.sort_index(ascending=False, inplace=True)

            df = df[:100]

            df.sort_index(ascending=True, inplace=True)

            return df

        return pd.DataFrame()

    def stat_reply(self, symbol: Coin) -> str:
        """Gathers most recent prices for given token from ByBit API.

        Parameters
        ----------
        symbol : Coin

        Returns
        -------
        str
            Preformatted markdown.
        """
        if data := self.session.latest_information_for_symbol(
                symbol=symbol.symbol + self.vs_currency
        )['result']:

            now_price = data['lastPrice']
            open_price = data['openPrice']
            high_price = data['highPrice']
            low_price = data['lowPrice']
            one_hr_change = self.get_one_hour_change(symbol, now_price)
            twen_four_hr_change = (float(now_price) / float(open_price) - 1) * 100

            title = f"24h {symbol.symbol} Stats:\n\n"
            current_price = f"Current price: ${now_price}\n"
            _open = f"Open: ${open_price}\n"
            high = f"High: ${high_price}\n"
            low = f"Low: ${low_price}\n"
            one_change = f"1h Change: {one_hr_change:.2f}%\n"
            twenty_four_change = f"24h Change: {twen_four_hr_change:.2f}%\n"

            return title + current_price + _open + high + low + one_change + twenty_four_change

        else:
            return f"The price for {symbol.symbol} is not available. If you suspect this is an error run `/status`"

