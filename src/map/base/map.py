import pygame
from pydantic import BaseModel
from .tile import BaseTile


class BaseMap(BaseModel):
    """
    Define the base configuration for the map
    """

    tiles: list[BaseTile]

    def render(self, tile_size: int = 64) -> pygame.Surface:
        """
        Render the map tiles in a grid onto a pygame surface.

        Each tile's terrain image (from rural_details.terrain.base_image) is
        scaled to tile_size and blitted at the grid position determined by
        the tile's rural_details.coordinates.

        Args:
            tile_size (int): The pixel size of each tile edge. Defaults to 64.

        Returns:
            pygame.Surface: A surface containing the rendered map grid.
        """
        max_x = max(tile.rural_details.coordinates.x for tile in self.tiles)
        max_y = max(tile.rural_details.coordinates.y for tile in self.tiles)
        grid_w = max_x + 1
        grid_h = max_y + 1

        surface = pygame.Surface(
            (grid_w * tile_size, grid_h * tile_size), pygame.SRCALPHA
        )

        for tile in self.tiles:
            x = tile.rural_details.coordinates.x
            y = tile.rural_details.coordinates.y
            image = tile.rural_details.terrain.base_image

            scaled = pygame.transform.smoothscale(image, (tile_size, tile_size))

            rotation = tile.rural_details.rotation
            if rotation:
                scaled = pygame.transform.rotate(scaled, -rotation)

            surface.blit(scaled, (x * tile_size, y * tile_size))

        return surface
