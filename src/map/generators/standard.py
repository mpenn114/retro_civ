from src.map.base.generator import BaseMapGenerator
from src.map.base.map_size import BaseMapSize
from src.map.base.map import BaseMap
from pydantic import BaseModel
import numpy as np

class StandardMapParameters(BaseModel):
    """
    Define the parameters for the standard map

    Note: all distance / length parameters are in units of tiles
    """
    # Define the map size
    map_size: BaseMapSize = BaseMapSize(size_x=500, size_y=300)

    # Define the number of islands to seed (note: islands may merge so there could
    # be fewer than {island_seeds} islands)
    island_seeds: int = 10

    # Define the mean and variance parameters for the radius and eccentricity of the islands
    # Note: We assume that log(radius) = N(log(mu), sigma^2)
    island_radius_mean = 50
    log_island_radius_variance = 2

    # Define the 




class StandardMapGenerator(BaseMapGenerator):

    def __init__(self, map_params: StandardMapParameters):
        """
        Generate a new map of a certain type

        Args:
            map_params (StandardMapParameters): The parameters for the map (e.g. size)
        """
        self.params = map_params

    def generate(self) -> BaseMap:
        """
        Generate a standard map

        We perform the following procedure:

        1) Seed islands
        2) Select each island shape as a Gaussian-perturbed ellipse
        3) Add shallow and deep water to the non-island spaces accordingly 
        4) Use a baseline model for terrain type, based on features of the tile (distance to sea, latitude etc.)
        5) Choose an arbitrary point in each island and assign its terrain based on this model
        6) Assign remaining terrains based on this model, with a penalty assigned for terrain transitions
        7) Add rivers

        Args:
            map_size (BaseMapSize): The size of the map
        
        Returns:
            BaseMap: The map object
        """


    def _generate_islands(self) -> np.ndarray:
        """
        Generate islands for the map

        Returns:
            np.ndarray: A boolean mask determining whether or not a tile is land
        """
        # Initialise the mask
        land_tiles = np.zeros(self.params.map_size.size).astype(bool)

        # Choose 

        
