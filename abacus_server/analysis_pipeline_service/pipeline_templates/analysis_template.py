import typing


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
        self.name_tag = None

    def run(self, input):
        """Insert analysis here"""

        return input
