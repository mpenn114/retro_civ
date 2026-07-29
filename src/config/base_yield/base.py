from pydantic import BaseModel, Field


class BaseYield(BaseModel):
    """
    Define a base class for determining the base yield of a terrain

    Note: This applies before any resources or improvements are taken into account
    """

    food: int = Field(ge=0, le=4)
    production: int = Field(ge=0, le=4)
    gold: int = Field(ge=0, le=4)
    happiness: int = Field(ge=0, le=4)
    science: int = Field(ge=0, le=4)
    culture: int = Field(ge=0, le=4)
