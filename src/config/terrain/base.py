from pydantic import BaseModel, Field
from src.config.base_yield.base import BaseYield
from src.config.resources.base import BaseResource
import pygame


class BaseTerrain(BaseModel):
    """
    Define a base class for storing different types of terrain
    """

    # Give the human-readable name of the terrain
    name: str

    # Give the movement cost of the terrain
    movement_cost: int = Field(ge=0, le=4)

    # Determine if the terrain ends movement
    ends_movement: bool = False

    # Give the defensive multiplier of the terrain
    defensive_multiplier: float = Field(ge=0, le=3)

    # Determine if the terrain is land or sea
    is_land: bool

    # Give the base yield of the terrain (before any resources are added)
    base_yield: BaseYield

    # Give the resource, if any, that is on this terrain
    resource: BaseResource | None

    # Give the base image for this terrain
    base_image: pygame.Surface
