import numpy as np
from pydantic import BaseModel, Field

class EllipseParams(BaseModel):
    """
    Define the parameters for the ellipse

    centre: (x, y) coordinates of the ellipse centre.
    radius: Semi-major axis length.
    eccentricity: Ellipse eccentricity, between 0 and 1.

    """
    centre: tuple[float, float]
    radius: float = Field(ge=0)
    eccentricity: float = Field(ge = 0, le = 1)

class PerturbedEllipse:

    def __init__(self, params: EllipseParams):
        """
        Create a configurable ellipse 

        Args:
            params (EllipseParams): The parameters for the ellipse
        """
        self.params = params

    def perturb(
        self,
        perturbation_variance:float,
        n_points: int = 1000
    ) -> np.ndarray:
        """
        Generate evenly spaced points around an ellipse perimeter that is perturbed by a Gaussian kernel

        Note: We impose that the noise integrates to 0 to ensure a closed shape

        Args:
            n_points (int): The number of points to get  
            
        Returns:
            Array of shape (n_points, 2) containing x, y coordinates.
        """

        # Unpack the parameters and convert to 
        cx, cy = self.params.centre
        a = self.params.radius
        b = a * np.sqrt(1 - self.params.eccentricity**2)

        # Generate the angular grid
        theta = np.linspace(0, 2 * np.pi, n_points)

        # Generate the noise
        raw_noise = np.random.randn(size=n_points)*np.sqrt(perturbation_variance)/n_points
        centred_multiplicative_noise = np.exp(raw_noise - raw_noise.mean())

        # Generate the points
        ellipse_points = np.zeros((n_points, 2))
        ellipse_points[:,0] = cx + a * centred_multiplicative_noise * np.cos(theta)
        ellipse_points[:,1] = cy + b * centred_multiplicative_noise * np.sin(theta)

        return ellipse_points