class DataSource:
    def __init__(self) -> None:
        """
        This is a template for creating a DataSource object. 

        Example target_function 
        [{"name": "get_product_candles",
        "kwargs": {"product_id": "BTC-USD"},
        "recall_interval": None,
        "analysis_bypass": False},
        {"name": "get_product_order_book",
        "kwargs": {"product_id": "BTC-USD"},
        "recall_interval": None,
        "analysis_bypass": True
        }
        ] """

        # Name to represent this analysis pipeline
        self.name_tag: str = None

        # Service to request data from Exp: crypto_service
        self.service_name: str = None

        # Will this be a websocket or https request
        self.request_type: str = None

        # What is the name of the function(owned by the above service) that should be called to retrive data
        """Individual target function should follow the schema
        {"name":str         name of the function in a service that should be called
            "kwargs":dict   Keyword args that are to be passed through the target function
            "recall_interval":int   how frequently should the target_function get called. Used for polling an api using https requests}
            "analysis_bypass":bool      Use true to indicate to analysis manager that an analysis is not required for the data returned by this target_function. Data will be sent straight through analysis manager to decision manager"""
        self.target_functions: list = None

    def data_filter(data):
        """Can create a filter algorithm for a data source"""
        return data
