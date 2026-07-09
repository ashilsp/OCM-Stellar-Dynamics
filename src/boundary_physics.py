"""
OCM-Stellar-Dynamics: Manifold Viscosity & Drag Tensor Solver
"""

import numpy as np
from src.constants import DEFAULT_ETA_M

class ManifoldViscositySolver:
    """
    Calculates the boundary layer metric spring updates (\tau_{M,\mu\nu})
    to suppress Poincaré instabilities and maintain coplanar/resonant trajectories.
    """
    
    def __init__(self, eta_m: float = DEFAULT_ETA_M):
        self.eta_m = eta_m

    def compute_manifold_drag_force(self, 
                                    velocities: np.ndarray, 
                                    perturbation_vectors: np.ndarray) -> np.ndarray:
        """
        Evaluates the metric spring restoration force:
        \nabla^\mu \tau_{M, \mu\nu} \propto \eta_M \cdot S_\nu
        
        Parameters:
            velocities (np.ndarray): Velocities of bodies, shape (N, 3).
            perturbation_vectors (np.ndarray): Non-axial perturbation vector S_\nu, shape (N, 3).
            
        Returns:
            np.ndarray: Restorative acceleration array of shape (N, 3).
        """
        # Non-linear spike response when perturbation exceeds baseline metric threshold
        perturbation_mag = np.linalg.norm(perturbation_vectors, axis=1, keepdims=True)
        nonlinear_viscosity = self.eta_m * (1.0 + perturbation_mag**2)
        
        # Localized metric restoration torque / drag force
        drag_force = - nonlinear_viscosity * perturbation_vectors
        return drag_force
