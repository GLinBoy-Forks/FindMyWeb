from enum import Enum

from pydantic import BaseModel


class ResponseStates(Enum):
    OK = "OK"


class StatusResponse(BaseModel):
    status: ResponseStates


class OKStatusResponse(StatusResponse):
    status: ResponseStates = ResponseStates.OK
