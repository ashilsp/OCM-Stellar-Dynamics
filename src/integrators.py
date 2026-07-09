"""
OCM-Stellar-Dynamics: Adaptive RK4 Metric-Flow Integrator (SM1)
Executes geodesic numerical integrations governed by the micro-nodal routing matrix (c_ij)
and localized manifold drag tensor (\tau_{M,\mu\nu}).
"""

import numpy as np
from typing import Callable, Tuple, Dict
from src.constants import DEFAULT_ETA_M

def ocm_geodesic_acceleration(positions: np.ndarray, 
                             velocities: np.ndarray, 
                             masses: np.ndarray, 
                             c_matrix: np.ndarray, 
                             eta_m: float = DEFAULT_ETA_M) -> np.ndarray:
    """
    Computes modified OCM accelerations:
    d^2 x^\\alpha / d\\lambda^2 + \\Gamma^\\alpha_{\\mu\\nu} dx^\\mu/d\\lambda dx^\\nu/d\\lambda = -\\nabla^\\alpha \\tau_{M,\\mu\\nu}

    Parameters:
        positions (np.ndarray): Shape (N, 3) positions in AU.
        velocities (np.ndarray): Shape (N, 3) velocities in AU/yr.
        masses (np.ndarray): Shape (N,) masses in Solar Masses.
        c_matrix (np.ndarray): Micro-nodal routing matrix (c_ij) constraints.
        eta_m (float): Localized manifold viscosity parameter.

    Returns:
        np.ndarray: Acceleration vectors for N bodies.
    """
    n_bodies = len(masses)
    accelerations = np.zeros_like(positions)
    
    # G in units of AU^3 / (Solar Mass * yr^2)
    G_const = 4 * np.pi**2
    
    for i in range(n_bodies):
        acc_i = np.zeros(3)
        for j in range(n_bodies):
            if i == j:
                continue
            r_vec = positions[j] - positions[i]
            r_mag = np.linalg.norm(r_vec) + 1e-12
            
            # Classical Newtonian term weighted by micro-nodal coefficient c_ij
            c_ij = c_matrix[i, j] if i < c_matrix.shape[0] and j < c_matrix.shape[1] else 1.0
            newtonian_acc = (G_const * masses[j] * r_vec) / (r_mag**3) * c_ij
            
            # Localized Manifold Drag Restoration (- \nabla^\alpha \tau_{M,\mu\nu})
            v_rel = velocities[i] - velocities[j]
            shear_s = v_rel / (r_mag + 1e-6)
            viscous_spike = eta_m * (1.0 + np.linalg.norm(shear_s)**2)
            manifold_drag_acc = - viscous_spike * shear_s
            
            acc_i += newtonian_acc + manifold_drag_acc
            
        accelerations[i] = acc_i
        
    return accelerations

def adaptive_rk4_step(positions: np.ndarray, 
                      velocities: np.ndarray, 
                      masses: np.ndarray, 
                      c_matrix: np.ndarray, 
                      dt: float, 
                      eta_m: float = DEFAULT_ETA_M) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    4th-Order Adaptive Runge-Kutta step with dynamic time-stepping to capture viscosity spikes.
    """
    # RK4 Stage 1
    k1_v = ocm_geodesic_acceleration(positions, velocities, masses, c_matrix, eta_m)
    k1_x = velocities
    
    # RK4 Stage 2
    k2_v = ocm_geodesic_acceleration(positions + 0.5 * dt * k1_x, velocities + 0.5 * dt * k1_v, masses, c_matrix, eta_m)
    k2_x = velocities + 0.5 * dt * k1_v
    
    # RK4 Stage 3
    k3_v = ocm_geodesic_acceleration(positions + 0.5 * dt * k2_x, velocities + 0.5 * dt * k2_v, masses, c_matrix, eta_m)
    k3_x = velocities + 0.5 * dt * k2_v
    
    # RK4 Stage 4
    k4_v = ocm_geodesic_acceleration(positions + dt * k3_x, velocities + dt * k3_v, masses, c_matrix, eta_m)
    k4_x = velocities + dt * k3_v
    
    # State update
    new_positions = positions + (dt / 6.0) * (k1_x + 2*k2_x + 2*k3_x + k4_x)
    new_velocities = velocities + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
    
    # Adaptive time-step adjustment based on maximum acceleration change
    max_acc_change = np.max(np.abs(k4_v - k1_v))
    next_dt = dt * 0.9 * (1.0 / (max_acc_change + 1e-10))**0.2
    next_dt = np.clip(next_dt, 1e-5, 0.1)  # Bound time-step between 1e-5 and 0.1 years
    
    return new_positions, new_velocities, float(next_dt)
