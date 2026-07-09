"""
OCM-Stellar-Dynamics: Micro-Tensor Field Formalism Engine
Calculates effective stress-energy tensors, manifold drag tensors, 
and non-linear viscous restoration torque for stellar systems.
"""

import numpy as np
from src.constants import DEFAULT_ETA_M

def compute_effective_stress_energy(t_baryon: np.ndarray, tau_m: np.ndarray) -> np.ndarray:
    """
    Computes the effective stress-energy tensor:
    T^{\\eff}_{\\mu\\nu} = T^{\\baryon}_{\\mu\\nu} + \\tau_{M, \\mu\\nu}

    Parameters:
        t_baryon (np.ndarray): Classical baryonic stress-energy matrix of shape (4, 4).
        tau_m (np.ndarray): Manifold drag tensor matrix of shape (4, 4).

    Returns:
        np.ndarray: Combined effective stress-energy tensor of shape (4, 4).
    """
    return t_baryon + tau_m

def compute_shear_restoration_torque(shear_vector_s: np.ndarray, 
                                      eta_m: float = DEFAULT_ETA_M) -> np.ndarray:
    """
    Calculates the quantized torsional restoration torque:
    \\nabla^{\\mu} \\tau_{M, \\mu\\nu} \\propto \\eta_M \\cdot S_{\\nu}

    Parameters:
        shear_vector_s (np.ndarray): Structural perturbation shear vector S_\\nu (3D or 4D array).
        eta_m (float): Localized manifold viscosity parameter.

    Returns:
        np.ndarray: Restorative metric spring vector opposing the perturbation.
    """
    s_norm = np.linalg.norm(shear_vector_s)
    
    # Non-linear viscous spike triggering at boundary perturbation thresholds
    viscous_spike = eta_m * (1.0 + np.power(s_norm, 2))
    
    # Restorative metric torque vector pointing back along the geometric corridor
    restoration_vector = - viscous_spike * shear_vector_s
    return restoration_vector
