from abc import ABC, abstractmethod
from .map import BaseMap

class BaseMapGenerator(ABC):

    def __init__(self):
        """
        Generate a new map of a certain type
        """

    @abstractmethod
    def generate(self) -> BaseMap:
        """
        Generate the map

        Args:
            map_size (BaseMapSize): The size of the map
        
        Returns:
            BaseMap: The map object
        """
        return BaseMap(tiles = set())