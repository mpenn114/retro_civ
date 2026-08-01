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
    island_seeds: int = Field(ge=0, default = 10)

    # Define the mean and variance parameters for the radius and eccentricity of the islands
    # Note: We assume that log(radius) = N(log(mu_r), sigma_r^2) and 
    # log(ecc/(1-ecc)) = N(log(mu_e/(1-mu_e)), sigma_e^2)
    island_radius_mean:float = Field(ge=0, default = 50.0)
    log_island_radius_variance:float = Field(ge=0, default = 2.0)
    min_island_radius: float = Field(ge=0, default = 1.0)
    max_island_radius: float = Field(ge=0, default = 100.0)

    island_ecc_mean:float = 0.3
    logit_island_ecc_variance:float = Field(ge=0, default = 1.0)

    # Define the island perturbation noise
    island_radius_perturbation_noise_mean:float = Field(ge=0, default = 25.0)
    island_radius_perturbation_noise_variance:float = Field(ge=0, default = 1.0)

    # Define the centre, amplitude, and noise of world temperature
    world_temperature_centre: float = 5.0
    world_temperature_amplitude: float = Field(ge=0, default=40.0)
    world_temperature_variance:float = Field(ge=0, default=16.0)

    # Determine the cooling effect of being near the coast (note: we have max*exp(-tile_distance/scale))
    water_cooling_scale:float = 1.0
    water_cooling_max:float = 5.0

    # Define the random seed
    seed:int = 42

