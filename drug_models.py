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


## WIP WIP WIP WIP
def drug_time_points(self, treatment_end: float) -> list[float]:
    """
    Provides drug simulation time points according to the protocol?? user input??
    
    """

    if self.dose_times:
        if self.treatment_end is not None:
            end = self.treatment_end
        else:
            end = treatment_end