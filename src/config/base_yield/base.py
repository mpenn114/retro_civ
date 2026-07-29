from pydantic import BaseModel, Field


class AdditiveYield(BaseModel):
    """
    Define a base class for determining the additive yield of an object
    """

    food: int = Field(ge=0, le=4, default=0)
    production: int = Field(ge=0, le=4, default=0)
    gold: int = Field(ge=0, le=4, default=0)
    happiness: int = Field(ge=0, le=4, default=0)
    science: int = Field(ge=0, le=4, default=0)
    culture: int = Field(ge=0, le=4, default=0)


class MultiplicativeYield(BaseModel):
    """
    Define a base class for determining the multiplicative yield of an object

    Note: this is a multipler on top of a yield - so for example, a multiplicative yield of 1.25
        means that the total additive yield of that category will be multiplied by 1.25.
    """

    food: float = Field(ge=0, le=2, default=1.0)
    production: float = Field(ge=0, le=2, default=1.0)
    gold: float = Field(ge=0, le=2, default=1.0)
    happiness: float = Field(ge=0, le=2, default=1.0)
    science: float = Field(ge=0, le=2, default=1.0)
    culture: float = Field(ge=0, le=2, default=1.0)
