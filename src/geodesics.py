"""
OCM-Stellar-Dynamics: Extended Geodesic Engine (SM2)
Computes the modified Christoffel connection \tilde{\Gamma}^\alpha_{\mu\nu}
and the structural correction tensor \Omega^\alpha_{\mu\nu}(c_{ij}).
"""

import numpy as np
from typing import Dict, Tuple

def compute_standard_christoffel(metric: np.ndarray, metric_derivative: np.ndarray) -> np.ndarray:
    """
    Computes standard Levi-Civita Christoffel symbols of the second kind:
    \Gamma^\alpha_{\mu\nu} = 1/2 * g^{\alpha\sigma} (\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu})

    Parameters:
        metric (np.ndarray): Metric tensor g_{\mu\nu} of shape (4, 4).
        metric_derivative (np.ndarray): Metric derivatives \partial_\sigma g_{\mu\nu} of shape (4, 4, 4).

    Returns:
        np.ndarray: Christoffel symbols \Gamma^\alpha_{\mu\nu} of shape (4, 4, 4).
    """
    g_inv = np.linalg.inv(metric)
    gamma = np.zeros((4, 4, 4))
    
    for alpha in range(4):
        for mu in range(4):
            for nu in range(4):
                val = 0.0
                for sigma in range(4):
                    term = (metric_derivative[mu, nu, sigma] + 
                            metric_derivative[nu, mu, sigma] - 
                            metric_derivative[sigma, mu, nu])
                    val += 0.5 * g_inv[alpha, sigma] * term
                gamma[alpha, mu, nu] = val
    return gamma

def compute_structural_correction_tensor(c_ij: np.ndarray, 
                                          potentials: np.ndarray, 
                                          grad_potentials: np.ndarray) -> np.ndarray:
    """
    Computes the micro-nodal structural correction tensor:
    \Omega^\alpha_{\mu\nu}(c_{ij}) = \sum_{i,j} c_{ij} ( \delta^\alpha_\mu \nabla_\nu \Phi_i \Phi_j + \delta^\alpha_\nu \nabla_\mu \Phi_j \Phi_i )

    Parameters:
        c_ij (np.ndarray): Micro-nodal routing matrix coefficients of shape (N, N).
        potentials (np.ndarray): Localized potentials \Phi_i for N stellar nodes.
        grad_potentials (np.ndarray): Gradient vectors \nabla \Phi_i of shape (N, 4).

    Returns:
        np.ndarray: Correction tensor \Omega^\alpha_{\mu\nu} of shape (4, 4, 4).
    """
    omega = np.zeros((4, 4, 4))
    n_nodes = len(potentials)
    
    for i in range(n_nodes):
        for j in range(n_nodes):
            weight = c_ij[i, j]
            phi_i = potentials[i]
            phi_j = potentials[j]
            grad_i = grad_potentials[i]
            grad_j = grad_potentials[j]
            
            for alpha in range(4):
                for mu in range(4):
                    for nu in range(4):
                        # Kronecker delta contractions \delta^\alpha_\mu and \delta^\alpha_\nu
                        term1 = (1.0 if alpha == mu else 0.0) * grad_i[nu] * phi_j
                        term2 = (1.0 if alpha == nu else 0.0) * grad_j[mu] * phi_i
                        omega[alpha, mu, nu] += weight * (term1 + term2)
                        
    return omega

def compute_extended_connection(gamma_standard: np.ndarray, 
                                omega_correction: np.ndarray) -> np.ndarray:
    """
    Calculates extended OCM metric connection:
    \tilde{\Gamma}^\alpha_{\mu\nu} = \Gamma^\alpha_{\mu\nu} + \Omega^\alpha_{\mu\nu}(c_{ij})
    """
    return gamma_standard + omega_correction
