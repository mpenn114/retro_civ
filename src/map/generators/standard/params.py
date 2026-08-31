from pydantic import BaseModel, Field
from src.map.base.map_size import BaseMapSize


class StandardMapParameters(BaseModel):
    """
    Define the parameters for the standard map

    Note: all distance / length parameters are in units of tiles
    """

    # Define the map size
    map_size: BaseMapSize = BaseMapSize(size_x=500, size_y=300)

    # Define the number of islands to seed (note: islands may merge so there could
    # be fewer than {island_seeds} islands)
    island_seeds: int = Field(ge=0, default=10)

    # Define the mean and variance parameters for the radius and eccentricity of the islands
    # Note: We assume that log(radius) = N(log(mu_r), sigma_r^2) and
    # log(ecc/(1-ecc)) = N(log(mu_e/(1-mu_e)), sigma_e^2)
    island_radius_mean: float = Field(ge=0, default=50.0)
    log_island_radius_variance: float = Field(ge=0, default=2.0)
    min_island_radius: float = Field(ge=0, default=1.0)
    max_island_radius: float = Field(ge=0, default=100.0)

    island_ecc_mean: float = 0.3
    logit_island_ecc_variance: float = Field(ge=0, default=1.0)

    # Define the island perturbation noise
    island_radius_perturbation_noise_mean: float = Field(ge=0, default=25.0)
    island_radius_perturbation_noise_variance: float = Field(ge=0, default=1.0)

    # Define the centre, amplitude, and noise of world temperature
    world_temperature_centre: float = 5.0
    world_temperature_amplitude: float = Field(ge=0, default=40.0)
    world_temperature_variance: float = Field(ge=0, default=16.0)

    # Determine the cooling effect of being near the coast (note: we have max*exp(-tile_distance/scale))
    water_cooling_scale: float = 1.0
    water_cooling_max: float = 5.0

    # Determine the probability of a tile being a mountain range seed
    mountain_range_seed_prob: float = Field(ge=0, default=0.002)

    # Determine the probability of a tile being a hill range seed
    hill_range_seed_prob: float = Field(ge=0, default=0.005)

    # Determine the probability of a tile being a river seed (note: rivers must be seeded on hills)
    river_seed_prob: float = Field(ge=0, default=0.05)

    # Determine the probability of continuing in the mountain range random walk
    mountain_range_continue_prob: float = Field(ge=0, le=1, default=0.6)
    hill_range_continue_prob: float = Field(ge=0, le=1, default=0.8)

    # Determine the probability of an orthogonally adjacent tile to a mountain being a hill
    hill_orthogonal_prob: float = Field(ge=0, le=1, default=0.3)

    # Define the random seed
    seed: int = 42
