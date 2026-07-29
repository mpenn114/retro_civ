from pydantic import BaseModel, Field


class BaseCoordinates(BaseModel):
    """
    Define a base for (x,y) coordinates
    """

    x: int = Field(ge=0)
    y: int = Field(ge=0)
