from pydantic import BaseModel
import numpy as np
from shapely import Polygon, Point
from shapely.strtree import STRtree

class ClassifiedTiles(BaseModel):
    """
    Determine the land/ coast /shallow ocean / deep ocean status of a map
    """
    coordinates: np.ndarray
    is_interior: np.ndarray
    is_coastal: np.ndarray
    is_shallow_ocean: np.ndarray
    is_deep_ocean: np.ndarray


class LandClassifier:

    def __init__(self):
        """
        Determine the status of tiles based on island polygons
        """

    def classify(self, islands:list[Polygon]) -> ClassifiedTiles:
        """
        Generate a land type classifier for the map

        Args:
            islands (list[Polygon]): The list of islands for the map

        Returns:
            ClassifiedTiles: Containing masks to determine if points are interior, coastal,
                shallow water or deep water
        """

    def _is_land(self,islands:list[Polygon], point:Point) -> bool:
        """
        Determine if a point is on land or not

        Args:
            islands (list[Polygon]): The islands
            point (Point): The point to test
        """
        return any(island.contains(point) for island in islands)