from pydantic import BaseModel, ConfigDict
import numpy as np
import shapely
from shapely import Polygon
from src.map.base.map_size import BaseMapSize


class ClassifiedTiles(BaseModel):
    """
    Determine the land/ coast /shallow ocean / deep ocean status of a map
    """

    coordinates: np.ndarray
    is_interior: np.ndarray
    is_coastal: np.ndarray
    is_shallow_ocean: np.ndarray
    is_deep_ocean: np.ndarray

    # Allow np.ndarrays
    model_config = ConfigDict(arbitrary_types_allowed=True)


class LandClassifier:
    def __init__(self):
        """
        Determine the status of tiles based on island polygons
        """

    def classify(
        self, islands: list[Polygon], map_size: BaseMapSize
    ) -> ClassifiedTiles:
        """
        Generate a land type classifier for the map

        Args:
            islands (list[Polygon]): The list of islands for the map
            map_size (BaseMapSize): The parameters containing the size of the map

        Returns:
            ClassifiedTiles: Containing masks to determine if points are interior, coastal,
                shallow water or deep water
        """
        # Generate the coordinates at the centre of each tile
        coordinates = (
            np.indices((map_size.size_y, map_size.size_x))
            .transpose(1, 2, 0)
            .astype(float)
            + 0.5
        )

        # Determine which points are land-based
        land_mask = self._determine_land(coordinates, islands)

        # Determine coastal and interior tiles
        is_coastal, is_interior = self._determine_coast(land_mask, map_size)

        # Determine shallow and deep tiles
        is_shallow, is_deep = self._determine_water_type(land_mask, map_size)

        return ClassifiedTiles(
            coordinates=coordinates,
            is_interior=is_interior,
            is_coastal=is_coastal,
            is_shallow_ocean=is_shallow,
            is_deep_ocean=is_deep,
        )

    def _determine_water_type(self, land_mask: np.ndarray, map_size: BaseMapSize):
        """
        Determine whether water tiles are deep or shallow water

        Note: Deep water tiles are more than two tiles from the coast

        Args:
            land_mask (np.ndarray): The mask determining whether tiles are land or sea
            map_size (BaseMapSize): The map size parameters

        Returns:
            np.ndarray: Determining if a tile is shallow water
            np.ndarray: Determining if a tile is deep water
        """
        # Get the water mask
        water = ~land_mask

        # Determine tiles which are within one tile of the land
        within_one = self._expand_mask_orthogonally(
            land_mask,
            map_size.wrap_x,
            map_size.wrap_y,
        )

        # Determine tiles which are within two tiles of the land
        within_two = self._expand_mask_orthogonally(
            within_one,
            map_size.wrap_x,
            map_size.wrap_y,
        )

        # Get the shallow and deep masks
        is_shallow = water & within_two
        is_deep = water & ~within_two

        return is_shallow, is_deep

    def _expand_mask_orthogonally(
        self,
        mask: np.ndarray,
        wrap_x: bool,
        wrap_y: bool,
    ) -> np.ndarray:
        """
        Expand a mask by one orthogonal tile.

        Args:
            mask (np.ndarray): Boolean mask to expand.
            wrap_x (bool): Whether the x-axis wraps.
            wrap_y (bool): Whether the y-axis wraps.

        Returns:
            np.ndarray: Expanded boolean mask.
        """
        if wrap_y:
            north = np.roll(mask, 1, axis=0)
            south = np.roll(mask, -1, axis=0)
        else:
            north = np.zeros_like(mask)
            south = np.zeros_like(mask)
            north[1:] = mask[:-1]
            south[:-1] = mask[1:]

        if wrap_x:
            west = np.roll(mask, 1, axis=1)
            east = np.roll(mask, -1, axis=1)
        else:
            west = np.zeros_like(mask)
            east = np.zeros_like(mask)
            west[:, 1:] = mask[:, :-1]
            east[:, :-1] = mask[:, 1:]

        return mask | north | south | east | west

    def _determine_coast(
        self, land_mask: np.ndarray, map_size: BaseMapSize
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Determine which tiles correspond to coast

        This is done by padding the land in each orthogonal direction

        Args:
            land_mask (np.ndarray): The mask determining whether or not a tile is land
            map_size (BaseMapSize): The map size parameters, including the wrapping parameters

        Returns:
            np.ndarray: Determining if the land is coastal
            np.ndarray: Determining if the land is part of an island interior
        """
        # Pad the land north and south
        if map_size.wrap_y:
            north = np.roll(land_mask, 1, axis=0)
            south = np.roll(land_mask, -1, axis=0)
        else:
            north = np.zeros_like(land_mask)
            south = np.zeros_like(land_mask)

            north[1:] = land_mask[:-1]
            south[:-1] = land_mask[1:]

        # Pad the land east and west
        if map_size.wrap_x:
            west = np.roll(land_mask, 1, axis=1)
            east = np.roll(land_mask, -1, axis=1)
        else:
            west = np.zeros_like(land_mask)
            east = np.zeros_like(land_mask)

            west[:, 1:] = land_mask[:, :-1]
            east[:, :-1] = land_mask[:, 1:]

        # Determine the interior
        is_interior = land_mask & north & south & east & west
        is_coastal = land_mask & ~is_interior

        return is_coastal, is_interior

    def _determine_land(self, coordinates: np.ndarray, islands: list[Polygon]):
        """
        Determine which points are land

        Args:
            coordinates (np.ndarray): Array of size (m,n,2) of tile centre coordinates
            islands (list[Polygon]): The islands on the map

        Returns:
            np.ndarray: A boolean mask determining whether points are land
        """
        # Generate the shapely points
        points = shapely.points(
            coordinates[..., 0].ravel(),
            coordinates[..., 1].ravel(),
        )

        land = np.zeros(len(points), dtype=bool)

        # Classify whether the points are land
        for island in islands:
            land |= shapely.contains(island, points)

        land = land.reshape(coordinates.shape[:2])

        return land
