from pydantic import BaseModel, Field
from src.config.base_yield.base import AdditiveYield
import pygame


class BaseTerrain(BaseModel):
    """
    Define a base class for storing different types of terrain
    """

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
