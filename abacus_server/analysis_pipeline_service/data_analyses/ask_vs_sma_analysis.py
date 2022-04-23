import typing
from pandas import DataFrame


class DataAnalysis:
    """
    Template class to create a DataAnalysis object.

    Requirements:
        name_tag: str should match the name_tag property to the DataSouce that is retrieving data for this analysis.

        run():
            run function is what is called by the data_analysis_manager. What is return by the run function is what will be sent to the data_decision_manager
            raw data from a DataSource object is recieved in the run function as input

    For custom functions that are used in an analysis add them to the class under the run function



    """

    def __init__(self) -> None:
        self.name_tag = "AskVsSma"

    def run(self, input):
        """Insert analysis here"""
        data = input['source_results']
        if 'get_product_candles' in data:
            print(f"RUNNING {self.name_tag} ANALYSIS")
            dict_candles = self.cbpro_cans_to_dict(
                candles=data['get_product_candles'])
            df = self.candles_to_df(candles=dict_candles)
            df['moving_avg'] = df['close'].rolling(30).mean()
            last_value = df.iloc[-1]
            return last_value['moving_avg']

    def cbpro_cans_to_dict(self, candles: list):

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

    def candles_to_df(self, candles: list):
        """Args:
                candles: list   list containing dictionaries which represent price candles"""

        cans_df = DataFrame(candles)
        return cans_df
