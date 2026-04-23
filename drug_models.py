"""
Defines how the drug behaves in the model and affects the cell population.
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class DrugProtocol:
    drug_name: str
    doseage: float # in uM
    dose_interval: float
    dose_times: list[float]
    elimination_rate: float
    treatment_start: float
    treatment_end: float


def drug_time_points(self, treatment_end: float) -> list[float]:
    """
    Provides drug simulation time points according to the protocol?? user input??
    
    """
    if self.dose_times:
        if self.treatment_end is not None:
            end = self.treatment_end
        else:
            end = treatment_end

def concentration_ode(t: float, C: float, protocol: DrugProtocol) -> float:
    """
    ODE right-hand side for the drug compartment (called by the solver
    between dose events).
 
    dC/dt = -k_elim * C
 
    Parameters
    t : float
        Current time (days): unused here but required by solve_ivp signature.
    C : float
        Current drug concentration in micromolar.
    protocol : DrugProtocol
        Treatment parameters.
 
    Returns
    float
        Rate of change of concentration.
    """
    return -protocol.elimination_rate * C