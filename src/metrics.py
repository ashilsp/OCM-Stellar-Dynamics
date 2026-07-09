"""
OCM-Stellar-Dynamics: Micro-Nodal Matrix & Metric Connection Solver
"""

import numpy as np
from src.constants import G_CONST, C_LIGHT

class MicroNodalMatrix:
    """
    Evaluates the localized micro-nodal space-time routing matrix (c_ij)
    and structural correction tensor (\Omega^\alpha_{\mu\nu}) that locks
    multi-star systems into non-chaotic geometric paths.
    """
    
    def __init__(self, n_bodies: int, weights: np.ndarray):
        """
        Parameters:
            n_bodies (int): Total stellar/planetary components in the system.
            weights (np.ndarray): Diagonal matrix weights c_ii for each node.
        """
        self.n_bodies = n_bodies
        self.weights = np.asfarray(weights)
        self.c_ij = self._initialize_routing_matrix()

    def _initialize_routing_matrix(self) -> np.ndarray:
        """
        Constructs the symmetric high-tension routing matrix c_ij across network nodes.
        """
        c_matrix = np.outer(self.weights, self.weights)
        np.fill_diagonal(c_matrix, self.weights)
        return c_matrix

    def compute_structural_correction(self, 
                                     positions: np.ndarray, 
                                     masses: np.ndarray) -> np.ndarray:
        """
        Computes the structural correction tensor \Omega^\alpha_{\mu\nu}(c_ij)
        arising from localized geometric potentials \Phi_i.
        
        Parameters:
            positions (np.ndarray): Array of shape (N, 3) representing body positions.
            masses (np.ndarray): Array of shape (N,) for stellar masses in kg.
            
        Returns:
            np.ndarray: Correction acceleration array of shape (N, 3).
        """
        n = self.n_bodies
        correction_accel = np.zeros_like(positions)
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                r_vec = positions[j] - positions[i]
                dist = np.linalg.norm(r_vec) + 1e-12
                
                # Localized node potential gradient
                grad_phi_j = (G_CONST * masses[j] / (dist**3)) * r_vec
                
                # Weighting acceleration by the micro-nodal coupling c_ij
                correction_accel[i] += self.c_ij[i, j] * grad_phi_j
                
        return correction_accel
