from pydantic import BaseModel, ConfigDict, Field
from src.config.base_yield.base import AdditiveYield
import pygame


class TerrainGeography(BaseModel):
    """
    Define the geographical parameters of different terrain types
    """

    # Give the temperature in degrees C
    temperature: int

    # Give the rainfall in a slightly vibes-based percentage scale
    rainfall: float = Field(ge=0, le=1)


class BaseTerrain(BaseModel):
    """
    Define a base class for storing different types of terrain
    """

    # Accept the pygame surface holding the sprite, which pydantic cannot validate itself
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Give the human-readable name of the terrain
    name: str

    # Give the movement cost of the terrain
    movement_cost: float = Field(ge=0, le=4)

    # Give the defensive multiplier of the terrain
    defensive_multiplier: float = Field(ge=0, le=3)

    # Determine if the terrain is land or sea
    is_land: bool

    # Determine if the terrain blocks sight and ranged attacks
    blocks: bool = False

    # Give the base yield of the terrain (before any resources are added)
    base_yield: AdditiveYield

    # Give the base image for this terrain
    base_image: pygame.Surface

    # Give the geography of this terrain, or None if it is independent of geography
    geography: TerrainGeography | None = None

    def with_image(self, base_image: pygame.Surface) -> "BaseTerrain":
        """
        Give a copy of this terrain that differs only in the sprite drawn for it

        Use this for tiles that play identically but are drawn differently, such as the corner
        piece of a river or a coastline, so the two can never drift apart

        Args:
            base_image (pygame.Surface): The sprite the copy is drawn with

        Returns:
            BaseTerrain: The terrain with its sprite replaced
        """
        return self.model_copy(update={"base_image": base_image})
