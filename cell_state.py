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

