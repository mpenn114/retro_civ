from pydantic import BaseModel, ConfigDict, Field


class BaseCoordinates(BaseModel):
    """
    Define a base for (x,y) coordinates
    """

    model_config = ConfigDict(frozen=True)

    x: int = Field(ge=0)
    y: int = Field(ge=0)
