from src.config.terrain import BaseTerrain, DesertTerrain, ForestTerrain, GrassTerrain, HillsTerrain, JungleTerrain, MountainTerrain, PlainsTerrain, SnowTerrain, TundraTerrain
from src.map.base.rural import BaseRural
import numpy as np
from .params import StandardMapParameters
from scipy.ndimage import distance_transform_edt

class StandardLandTerrainModel:

    def __init__(self):
        """
        Create a model to assign land to different parts of an island
        """
        self.flat_land_types = [
            DesertTerrain, ForestTerrain, GrassTerrain, JungleTerrain, PlainsTerrain, SnowTerrain, TundraTerrain
        ]
        self.hills = HillsTerrain
        self.mountains = MountainTerrain

    def assign_island_interior(self, interior_mask:np.ndarray, map_params:StandardMapParameters) -> set[BaseRural]:
        """
        Assign a land type to each tile

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                island (as coastal terrains do not need to be assigned)
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            set[BaseRural]: A set of rural tiles for the interior of the islands
        """
        # Get the temperatures
        tile_temperatures = self._create_tile_temperature(interior_mask, map_params)

        # Get the flat terrain
        flat_terrain_map = self._assign_flat_terrain(interior_mask, tile_temperatures)

        # Assign mountains, hills, and rivers


    def _assign_flat_terrain(self, interior_mask: np.ndarray, tile_temperatures:np.ndarray) -> dict[tuple[int,int], BaseTerrain]:
        """
        Assign a flat terrain land type to each tile

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                island (as coastal terrains do not need to be assigned)
            tile_temperatures (np.ndarray): The temperature of each tile

        Returns:
            dict[tuple[int,int], BaseTerrain]: Mapping each coordinate to the terrain type
        """

        # Get scales for each flat terrain in each tile
        terrain_probabilities = {
            terrain: self._get_terrain_tile_prob(tile_temperatures, terrain) for terrain in self.flat_land_types
        }

        # Get combined probability matrices
        probabilities = np.stack(
            [terrain_probabilities[terrain] for terrain in self.flat_land_types],
            axis=-1,
        )

        # Only sample interior tiles
        flat_probs = probabilities[interior_mask]

        # Normalise probabilities per tile
        flat_probs /= flat_probs.sum(axis=1, keepdims=True)

        # Generate random numbers per tile
        random_values = np.random.random(flat_probs.shape[0])

        # Convert probabilities into cumulative probabilities
        cumulative = np.cumsum(flat_probs, axis=1)

        # Pick the first terrain where cumulative probability exceeds random value
        terrain_indices = (cumulative > random_values[:, None]).argmax(axis=1)

        # Create the map from coordinates to terrain types
        terrain_map = {(x,y): self.flat_land_types[idx]
            for (y, x), idx in zip(
                np.argwhere(interior_mask),
                terrain_indices,
            )
        }

        return terrain_map

    

    def _get_terrain_tile_prob(self,temperature:np.ndarray, terrain:BaseTerrain):
        """
        Get the unscaled probability of each tile being each terrain

        We model this as simply 1/(squared difference)

        Args:
            temperature (np.ndarray) The by-tile temperature
            terrain (BaseTerrain): The terrain type
        """
        return 1/np.clip(np.square(temperature - terrain.geography.temperature), 0.25, np.inf)

    def _create_tile_temperature(self, interior_mask:np.ndarray,map_params:StandardMapParameters) -> np.ndarray:
        """
        Create an tile-level temperature

        Args:
            interior_mask (np.ndarray): Determining whether a tile is on the interior of an
                            island (as coastal terrains do not need to be assigned)
            map_params (StandardMapParameters): The parameters for the map

        Returns:
            np.ndarray: Containing the temperature of each tile
        """
        # Get the length of the map
        map_size_x =  map_params.map_size.size_x

        # Assign a baseline temperature for each x coordinate
        baseline_temperature = np.sin(np.pi*np.arange(map_size_x)/map_size_x)*map_params.world_temperature_amplitude + map_params.world_temperature_centre

        # Get the distance to water
        distance_to_water = 1 + distance_transform_edt(interior_mask)

        # Apply cooling for land near the coast
        coastal_cooling = map_params.water_cooling_max*np.exp(-distance_to_water / map_params.water_cooling_scale)

        # Create the overall temperature
        overall_tile_temperature = baseline_temperature[:, np.newaxis] + coastal_cooling + np.random.randn(interior_mask.shape)*np.sqrt(map_params.world_temperature_variance)

        return overall_tile_temperature
