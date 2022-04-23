

from datetime import datetime
from ...models.paper_trade_models import PaperTradeRequest
from ...global_events import global_events_manager
class DataDecision:
    """
    A template class for a DataDecision


    Requirements:
        name_tag:str Should match the DataSource and DataAnalysis that a decision is be made from.
        required_inputs:dict    A dictionary with keys containing the names of the target_functions 
                                from which data is required to make a decision. The value should always 
                                be set to None when init the class. After recieving the first signal from 
                                a target_function with data the data will be stored as the dict value. 
                                After the first signal, data sent in the last signal will always be stored 
                                in the dict value. This is where the data can be used in the run function. 

        run():
        the run function is called by the data_d    ecision_manager and will contain the code for what should be 
        done based on the analysis

    custom functions can be writen as part of the DataDecision class and be referenced in the run(): function.
        """

    def __init__(self) -> None:
        self.name_tag = "AskVsSma"
        self._required_inputs = {"get_product_order_book": {},
                                 "get_product_candles": {}}

        self.is_paper_trade = True

    @property
    def required_inputs(self):
        return self._required_inputs

    @required_inputs.setter
    def required_inputs(self, message: dict):
        data_source_t_func = list(message['source_results'].keys())[0]
        self._required_inputs[data_source_t_func] = message

    def has_enough_data(self):
        is_not_none = True
        print(self._required_inputs)
        for t_func in self.required_inputs:
            if not self.required_inputs[t_func]:
                is_not_none = False
        return is_not_none

    def update_input(self, key, message):
        now = datetime.now()
        self._required_inputs[key].update({now: message})

    def run(self):
        """To reference incoming data use
                self.required_inputs['NameOfYourTargetFunction']['Either source_results Or analysis_results]"""
        ask_price_results = list(
            self.required_inputs['get_product_order_book'].values())
        last_ask_price = ask_price_results[len(
            ask_price_results)-1]['source_results']['get_product_order_book']['asks'][0][0]

        sma_results = list(
            self.required_inputs['get_product_candles'].values())
        last_sma_price = sma_results[len(sma_results)-1]['analysis_results']
        print(f"MAKING {self.name_tag} DECISION")
        if float(last_ask_price) > float(last_sma_price):
            print(f"BUYING ask was {last_ask_price}, sma was {last_sma_price}")
            self.paper_buy_order(ticker="BTC", price=last_ask_price, quantity=10, sender=self.name_tag)

        else:
            print(
                f"NOT BUYING ask was {last_ask_price}, sma was {last_sma_price} ... ")

    

    def paper_buy_order(self, ticker: str, quantity: int, price: float, sender: str):
        buy_order = {
            "ticker": ticker,
            "buy_price": price,
            "quantity": quantity,
        }

        paper_trade_target_function = {
            "name": 'submit_buy_order',
            "kwargs": {"buy_order": buy_order}
        }
        ptr = PaperTradeRequest(target_function=paper_trade_target_function)

        global_events_manager.send_signal(
            service_name='paper_trading_service', sender=sender, message=ptr)
