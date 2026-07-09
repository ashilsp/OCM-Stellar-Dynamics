"""
OCM-Stellar-Dynamics: Physical and Metric Constants Module
"""

import numpy as np

# --- Fundamental Physical Constants (SI Units) ---
G_CONST = 6.67430e-11        # Gravitational constant [m^3 kg^-1 s^-2]
C_LIGHT = 2.99792458e8       # Speed of light in vacuum [m s^-1]
MSUN = 1.98847e30            # Solar Mass [kg]
AU = 1.495978707e11          # Astronomical Unit [m]
YEAR_SEC = 31557600.0        # Seconds in a Julian year

# --- OCM Metric Field Baseline Constants ---
DEFAULT_ETA_M = 1.0e-7       # Baseline manifold viscosity parameter
DEFAULT_HIGH_TENSION_K = 1.0 # Background metric spring tension coefficient
