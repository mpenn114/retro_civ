from src.map.base.generator import BaseMapGenerator
from src.map.base.map_size import BaseMapSize
from src.map.base.map import BaseMap
from src.map.utils.ellipse import PerturbedEllipse, EllipseParams
from pydantic import BaseModel
import numpy as np
from shapely import Polygon
from src.map.utils.land_classifier import LandClassifier
from shapely.strtree import STRtree

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
    # Note: We assume that log(radius) = N(log(mu_r), sigma_r^2) and 
    # log(ecc/(1-ecc)) = N(log(mu_e/(1-mu_e)), sigma_e^2)
    island_radius_mean:float = 50.0
    log_island_radius_variance:float = 2.0
    min_island_radius: float = 1.0
    max_island_radius: float = 100.0

    island_ecc_mean:float = 0.3
    logit_island_ecc_variance:float = 1.0

    # Define the island perturbation noise
    island_radius_perturbation_noise_mean:float = 25.0
    island_radius_perturbation_noise_variance:float = 1.0

    # Define the random seed
    seed = 42




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
        # Generate the islands
        islands = self._generate_islands()

        # Classify the land
        classified_land = LandClassifier().classify(islands)


    


    def _generate_islands(self) -> list[Polygon]:
        """
        Generate islands for the map

        Returns:
            list[Polygon]: A list of the islands on the map, as shapely polygons
        """

        # Generate islands in turn
        islands: list[Polygon] = []
        for _ in range(self.params.island_seeds):

            # Sample the centre of the island
            island_centre_x = np.random.choice(self.params.map_size.size_x)
            island_centre_y = np.random.choice(self.params.map_size.size_y)

            # Sample the radius and eccentricity of the island
            island_radius = np.clip(self.params.island_radius_mean*np.exp(np.random.randn()*np.sqrt(self.params.log_island_radius_variance)), self.params.min_island_radius, self.params.max_island_radius)
            logit_island_eccentricity = self.logit(self.params.island_ecc_mean) + np.random.randn()*np.sqrt(self.params.logit_island_ecc_variance)
            island_eccentricity = self.logistic(logit_island_eccentricity)

            # Sample the perturbation parameters
            island_perturbation_strength = np.clip(self.params.island_radius_perturbation_noise_mean + np.sqrt(self.params.island_radius_perturbation_noise_variance)*np.random.randn(), 0, np.inf)

            # Generate the ellipse parameters
            island_parameters = EllipseParams(centre=(island_centre_x, island_centre_y), radius = island_radius, eccentricity=island_eccentricity)

            # Generate the island ellipse
            island = PerturbedEllipse(island_parameters).perturb(island_perturbation_strength, n_points=20)

            # Add to the list of islands
            islands.append(Polygon(island))

        return islands






            



    @staticmethod
    def logit(x:np.ndarray) -> np.ndarray:
        """Get the logit of an array"""
        return np.log(x/(1-x))

    @staticmethod
    def logistic(x:np.ndarray) -> np.ndarray:
        """Get the logistic of an array"""
        return 1/(1+np.exp(-x))



        
