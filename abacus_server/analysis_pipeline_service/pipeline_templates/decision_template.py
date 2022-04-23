

from sqlalchemy import true


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
        the run function is called by the data_decision_manager and will contain the code for what should be 
        done based on the analysis

    custom functions can be writen as part of the DataDecision class and be referenced in the run(): function.
        """

    def __init__(self) -> None:
        self.name_tag: str = ""
        self._required_inputs: dict = {}
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
            if self.required_inputs[t_func] == None:
                is_not_none = False
        return is_not_none

    def run(self):
        """To reference incoming data use
                self.required_inputs['NameOfYourTargetFunction']['Either source_results Or analysis_results]"""
        pass
