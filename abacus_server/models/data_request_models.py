from pydantic import BaseModel, Field
import typing


class TargetFunction(BaseModel):
    name: str
    kwargs: dict


class ApiDataRequest(BaseModel):
    client: str = ""
    type: str = "https"
    target_function: TargetFunction = Field(
        name="",
        kwargs={}
    )


class ApiDataRequestRespone(BaseModel):
    name_tag: str
    content: typing.Any
    # params passed to target function
    tf_params: typing.Any
