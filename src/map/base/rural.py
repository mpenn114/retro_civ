from pydantic import BaseModel, ConfigDict, Field
from src.config.terrain import BaseTerrain
from src.config.improvements.base import BaseImprovement
from src.config.resources.base import BaseResource
from .coordinates import BaseCoordinates


class BaseRural(BaseModel):
    """
    Define a base class to contain all information about a rural tile
    """

    # Keep the model mutable but hashable, so tiles can be used as dict keys
    model_config = ConfigDict(eq=False)

    coordinates: BaseCoordinates
    terrain: BaseTerrain
    rotation: float = Field(ge=0, le=360, default=0.0)
    improvements: set[BaseImprovement] = set()
    resources: set[BaseResource] = set()

    def __eq__(self, other):
        if not isinstance(other, BaseRural):
            return NotImplemented
        return (
            self.coordinates == other.coordinates
            and self.terrain == other.terrain
            and self.rotation == other.rotation
            and self.improvements == other.improvements
            and self.resources == other.resources
        )

    def __hash__(self):
        return hash((
            self.coordinates,
            self.terrain,
            self.rotation,
            frozenset(self.improvements),
            frozenset(self.resources),
        ))

    def describe(self) -> str:
        """
        Describe the rural tile

        Returns:
            str: The description
        """
        return f"""
            Coordinates: ({self.coordinates.x, self.coordinates.y})
            Terrain: {self.terrain.name}
        """
