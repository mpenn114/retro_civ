from dataclasses import dataclass, fields
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
    coast_river: pygame.Surface
    coast: pygame.Surface
    deep_ocean: pygame.Surface
    desert: pygame.Surface
    forest_river_corner: pygame.Surface
    forest_river: pygame.Surface
    forest: pygame.Surface
    grass_river_corner: pygame.Surface
    grass_river: pygame.Surface
    grass: pygame.Surface
    hills_river_source: pygame.Surface
    hills: pygame.Surface
    jungle_river_corner: pygame.Surface
    jungle_river: pygame.Surface
    jungle: pygame.Surface
    mountain: pygame.Surface
    plains_river_corner: pygame.Surface
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


def _load_image_set[ImageSet](image_set: type[ImageSet], assets_path: Path) -> ImageSet:
    """
    Load every image an image set declares, taking each file name from its field name

    Args:
        image_set (type[ImageSet]): The image set to fill
        assets_path (Path): The directory the PNGs are read from

    Returns:
        ImageSet: The image set with every field loaded
    """
    return image_set(
        **{
            field.name: pygame.image.load(
                assets_path / f"{field.name}.png"
            ).convert_alpha()
            for field in fields(image_set)  # ty: ignore
        }
    )


import os
import pygame


os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()
pygame.display.set_mode((1, 1))
TERRAIN_IMAGES = _load_image_set(TerrainImages, TERRAIN_ASSETS_PATH)

UNIT_IMAGES = _load_image_set(UnitImages, UNIT_ASSETS_PATH)

__all__ = [TERRAIN_IMAGES, UNIT_IMAGES]
