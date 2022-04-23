from pandas import DataFrame
from .example_cbpro_candles import candles


def cbpro_cans_to_dict(candles: list):

    new_candles = []
    for candle in candles:
        can_dict = {"open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                    "timestamp": candle[0]}
        new_candles.append(can_dict)
    return new_candles


def candles_to_df(candles: list):
    """Args:
            candles: list   list containing dictionaries which represent price candles"""

    cans_df = DataFrame(candles)
    return cans_df


def run():
    cans = cbpro_cans_to_dict(candles=candles['content'])
    candle_df = candles_to_df(candles=cans)
    candle_df["moving_avg"] = candle_df['close'].rolling(8).mean()
    return candle_df['moving_avg'].iloc[-1]
