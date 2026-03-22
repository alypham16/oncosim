"""
Defining the properties of each cell subpopulation.
"""

from dataclasses import dataclass

@dataclass
class CellState:
    """
    A class representing the properties of a single marker-defined subpopulation.
    
    Attributes:

    proliferation_rate: How quickly a cell population divides and grows prior to drug treatment
    
    drug_resistance: A measure of how resistant the cell population is to the drug, usually represented 
    as a value between 0 and 1, where 0 means no resistance and 1 means complete resistance.
    
    ec50: the half-maximal effective concentration of the drug, in which the drug achieves 50% of its maximum effect on the cell population. 
    A lower EC50 indicates higher sensitivity to the drug, while a higher EC50 indicates lower sensitivity.
    
    max_kill_rate: the quickest the drug can kill the cell population, usually represented 0-1.
    
    transitions: a dictionary defining the probabilities of transitions between different cell states.
    The keys are the names of the states, while the values are the probabilities of transitioning to those states.

    """
    name: str
    proliferation_rate: float
    drug_resistance: float
    ec50: float
    max_kill_rate: float
    transitions: dict[str, float]  # transition probabilities to other states

    def effective_kill_rate(self, drug_concentration: float) -> float:
        """
        Uses the standard Hill equation formula:

        kill(C) = max_kill_rate * (C / (EC50 + C))

        given a drug concentration (C) to return the effective kill rate of the drug on this cell population. 
        
        Parameters:
        drug_concentration (float): The concentration of the drug being applied to the cell population.
        
        Returns:
        float: The effective kill rate of the drug on this cell population.
        """

        if drug_concentration <= 0:
            return 0

       # Implement Hill equation
        drug_effect = self.max_kill_rate * (drug_concentration / (self.ec50 + drug_concentration))
        
        # Adjust kill rate based on drug resistance
        effective_kill = drug_effect * (1 - self.drug_resistance)
        
        return effective_kill

def get_cell_states(cell_line:str) -> dict[str, CellState]:
    """
    Returns a dictionary of {surface_marker: CellState} for the supported cell line.
    For simplicity, the following supported states have hypothetical values. Only the surface-marker
    partitions (i.e. ESAM for MDA-MB-231, tetherin for MDA-MB-436) have been experimentally confirmed
    to help define subpopulations in lab.

    """

    ### Maybe make this so that users can change these based on their own experimental data?

    preset_cell_states = {
        "MDA-MB-231": {
            "ESAM high": CellState(
                name = "ESAM high",
                proliferation_rate = 0.5,
                drug_resistance = 0.15,
                ec50 = 0.8,
                max_kill_rate = 0.55,
                transitions = {"ESAM low": 0.03}),
                
            "ESAM low": CellState(
                name = "ESAM low",
                proliferation_rate = 0.3,
                drug_resistance = 0.65,
                ec50 = 2.5,
                max_kill_rate = 0.55,
                transitions = {"ESAM high": 0.01})
        },

        "MDA-MB-436": {
            "BST2 high": CellState(
                name = "BST2 high",
                proliferation_rate = 0.5,
                drug_resistance = 0.2,
                ec50 = 1.0,
                max_kill_rate = 0.6,
                transitions = {"non-BST2": 0.025}),

            "BST2 low": CellState(
                name = "BST2 low",
                proliferation_rate = 0.28,
                drug_resistance = 0.70,
                ec50 = 3.0,
                max_kill_rate = 0.6,
                transitions = {"BST2 high": 0.008})
        }
    }

    if cell_line not in preset_cell_states:
        raise ValueError(f"Unsupported cell line: {cell_line}. Supported cell lines are: {list(preset_cell_states.keys())}")
    
    return preset_cell_states[cell_line]
