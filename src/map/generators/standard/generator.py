from src.map.base.generator import BaseMapGenerator
from src.map.base.map import BaseMap
from src.map.base.tile import BaseTile
from src.map.utils.ellipse import PerturbedEllipse, EllipseParams
import numpy as np
from shapely import Polygon
from src.map.utils.land_classifier import LandClassifier
from .params import StandardMapParameters
from src.map.generators.standard.land_terrain_model import StandardLandTerrainModel


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
        8) Tidy with appropriate corner tiles to ensure congruity

        Args:
            map_size (BaseMapSize): The size of the map

        Returns:
            BaseMap: The map object
        """
        # Generate the islands
        islands = self._generate_islands()

        # Classify the land into islands and ocean
        classified_land = LandClassifier().classify(islands, self.params.map_size)

        # Fill in terrain
        generated_land = StandardLandTerrainModel().create_tiles(
            classified_land, self.params
        )

        # Create the map
        return BaseMap(
            tiles={BaseTile(rural_details=rural) for rural in generated_land}
        )

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
            island_radius = np.clip(
                self.params.island_radius_mean
                * np.exp(
                    np.random.randn() * np.sqrt(self.params.log_island_radius_variance)
                ),
                self.params.min_island_radius,
                self.params.max_island_radius,
            )
            logit_island_eccentricity = self.logit(
                self.params.island_ecc_mean
            ) + np.random.randn() * np.sqrt(self.params.logit_island_ecc_variance)
            island_eccentricity = float(self.logistic(logit_island_eccentricity))

            # Sample the perturbation parameters
            island_perturbation_strength = np.clip(
                self.params.island_radius_perturbation_noise_mean
                + np.sqrt(self.params.island_radius_perturbation_noise_variance)
                * np.random.randn(),
                0,
                np.inf,
            )

            # Generate the ellipse parameters
            island_parameters = EllipseParams(
                centre=(island_centre_x, island_centre_y),
                radius=island_radius,
                eccentricity=island_eccentricity,
            )

            # Generate the island ellipse
            island = PerturbedEllipse(island_parameters).perturb(
                island_perturbation_strength, n_points=20
            )

            # Add to the list of islands
            islands.append(Polygon(island))

        return islands

    @staticmethod
    def logit(x: np.ndarray | float) -> np.ndarray | float:
        """Get the logit of an array"""
        return np.log(x / (1 - x))

    @staticmethod
    def logistic(x: np.ndarray | float) -> np.ndarray | float:
        """Get the logistic of an array"""
        return 1 / (1 + np.exp(-x))
