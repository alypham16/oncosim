"""
Primary population dynamics simulation code (mathematical model).
Returns a history of cell counts for each state over time, in days.
"""

import numpy as np

def simulation(
        states: dict,
        initial_counts: dict,
        drug_name: str,
        dose: float,
        dose_interval_days: float,
        carrying_capacity: float,
        duration_days = 30) -> dict:
    
    counts = {name: float(initial_counts.get(name, 0)) for name in states}
    carrying_capacity = 1000000 # max total cells the simulator can handle
 
    history = {name: [] for name in states}
    history["days"] = list(range(duration_days + 1))
 
    for _ in range(duration_days):
        total = sum(counts.values())
 
        new_counts = {}
        for name, state in states.items():
            n = counts[name]
 
            # Mimics logistic growth model with a carrying capacity.
            growth = state.proliferation_rate * n * (1 - total / carrying_capacity)
 
            # Drug kills some cells
            cells_killed = state.kill_rate(dose) * n
 
            # Accounting for transition states
            leaving = sum(state.transitions.values()) * n
            arriving = sum(
                states[other].transitions.get(name, 0) * counts[other]
                for other in states if other != name)
 
            new_counts[name] = max(0, n + growth - cells_killed - leaving + arriving)
 
        counts = new_counts
        for name in states:
            history[name].append(round(counts[name]))
 
    # Initial values
    for name in states:
        history[name] = [initial_counts.get(name, 0)] + history[name]
 
    return history
 