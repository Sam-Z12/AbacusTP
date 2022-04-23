import typing
from pydantic import BaseModel


class DataAnalysisInput(BaseModel):
    name_tag: str
    source_results: typing.Any
    function_params: typing.Any


class DataDecisionInput(BaseModel):
    name_tag: str
    source_results: typing.Any
    function_params: typing.Any
    analysis_results: typing.Any
