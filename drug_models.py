"""
Defines how the drug behaves in the model and affects the cell population.
"""
import numpy as np
from dataclasses import dataclass

@dataclass
class DrugProtocol:
    drug_name: str
    doseage: float
    dose_interval: float
    elimination_rate: float
    treatment_duration: float