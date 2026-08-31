from pydantic import BaseModel, Field
from src.config.terrain import BaseTerrain
from src.config.improvements.base import BaseImprovement
from src.config.resources.base import BaseResource
from .coordinates import BaseCoordinates


class BaseRural(BaseModel):
    """
    Define a base class to contain all information about a rural tile
    """

    coordinates: BaseCoordinates
    terrain: BaseTerrain
    rotation: float = Field(ge=0, le=360, default=0.0)
    improvements: set[BaseImprovement] = set()
    resources: set[BaseResource] = set()
