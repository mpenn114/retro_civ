from dataclasses import dataclass
from pathlib import Path

import pygame


TERRAIN_ASSETS_PATH = Path("src/art/assets/terrain")
UNIT_ASSETS_PATH = Path("src/art/assets/units")


@dataclass(frozen=True)
class TerrainImages:
    """
    Store the images for each kind of terrain
    """

    coast_corner: pygame.Surface
    coast: pygame.Surface
    deep_ocean: pygame.Surface
    forest_river: pygame.Surface
    forest: pygame.Surface
    grass_river: pygame.Surface
    grass: pygame.Surface
    hills: pygame.Surface
    jungle_river: pygame.Surface
    jungle: pygame.Surface
    mountain: pygame.Surface
    plains_river: pygame.Surface
    plains: pygame.Surface
    shallow_ocean: pygame.Surface
    snow: pygame.Surface
    tundra: pygame.Surface


@dataclass(frozen=True)
class UnitImages:
    """
    Store the images for each kind of unit
    """

    settler: pygame.Surface
    warrior: pygame.Surface
    scout: pygame.Surface


TERRAIN_IMAGES = TerrainImages(
    coast_corner=pygame.image.load(
        TERRAIN_ASSETS_PATH / "coast_corner.png"
    ).convert_alpha(),
    coast=pygame.image.load(TERRAIN_ASSETS_PATH / "coast.png").convert_alpha(),
    deep_ocean=pygame.image.load(
        TERRAIN_ASSETS_PATH / "deep_ocean.png"
    ).convert_alpha(),
    forest_river=pygame.image.load(
        TERRAIN_ASSETS_PATH / "forest_river.png"
    ).convert_alpha(),
    forest=pygame.image.load(TERRAIN_ASSETS_PATH / "forest.png").convert_alpha(),
    grass_river=pygame.image.load(
        TERRAIN_ASSETS_PATH / "grass_river.png"
    ).convert_alpha(),
    grass=pygame.image.load(TERRAIN_ASSETS_PATH / "grass.png").convert_alpha(),
    hills=pygame.image.load(TERRAIN_ASSETS_PATH / "hills.png").convert_alpha(),
    jungle_river=pygame.image.load(
        TERRAIN_ASSETS_PATH / "jungle_river.png"
    ).convert_alpha(),
    jungle=pygame.image.load(TERRAIN_ASSETS_PATH / "jungle.png").convert_alpha(),
    mountain=pygame.image.load(TERRAIN_ASSETS_PATH / "mountain.png").convert_alpha(),
    plains_river=pygame.image.load(
        TERRAIN_ASSETS_PATH / "plains_river.png"
    ).convert_alpha(),
    plains=pygame.image.load(TERRAIN_ASSETS_PATH / "plains.png").convert_alpha(),
    shallow_ocean=pygame.image.load(
        TERRAIN_ASSETS_PATH / "shallow_ocean.png"
    ).convert_alpha(),
    snow=pygame.image.load(TERRAIN_ASSETS_PATH / "snow.png").convert_alpha(),
    tundra=pygame.image.load(TERRAIN_ASSETS_PATH / "tundra.png").convert_alpha(),
)

UNIT_IMAGES = UnitImages(
    settler=pygame.image.load(UNIT_ASSETS_PATH / "settler.png").convert_alpha(),
    warrior=pygame.image.load(UNIT_ASSETS_PATH / "warrior.png").convert_alpha(),
    scout=pygame.image.load(UNIT_ASSETS_PATH / "scout.png").convert_alpha(),
)

__all__ = [TERRAIN_IMAGES, UNIT_IMAGES]
