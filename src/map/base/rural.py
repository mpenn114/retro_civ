from pydantic import BaseModel
from src.config.terrain import BaseTerrain
from src.config.improvements.base import BaseImprovement
from src.config.resources.base import BaseResource


class BaseRural(BaseModel):
    """
    Define a base class to contain all information about a rural tile
    """

    terrain: BaseTerrain
    improvements: set[BaseImprovement] = set()
    resources: set[BaseResource] = set()
