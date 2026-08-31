from pydantic import BaseModel
from .tile import BaseTile


class BaseMap(BaseModel):
    """
    Define the base configuration for the map
    """

    tiles: list[BaseTile]
