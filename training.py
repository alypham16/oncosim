import argparse
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from cell_state import get_cell_states
from simulator import simulation

def training_data(states, n_samples = 500):
    state_names = list(states.keys())
    rng = np.random.default_rng(42)
    X, y = [], []
 
    for _ in range(n_samples):
        drug  = float(rng.uniform(0, 5))
        days  = int(rng.choice([14, 21, 30]))
        total = float(rng.uniform(10_000, 100_000))
        frac  = float(rng.uniform(0.1, 0.9))
 
        initial = {state_names[0]: total * frac,
                   state_names[1]: total * (1 - frac)}
 
        result = simulation(states, initial, drug, days)
 
        end_counts = {name: result[name][-1] for name in state_names}
        dominant = max(end_counts, key=end_counts.get)
        label = state_names.index(dominant)
 
        X.append([drug, frac, days])
        y.append(label)
 
    return np.array(X), np.array(y), state_names
 
states = get_cell_states("cell_states.json")
X, y, state_names = training_data(states)
 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, stratify = y, random_state = 1)
 
clf = LogisticRegression(random_state = 1)
clf.fit(X_train, y_train)
print(f"accuracy = {accuracy_score(y_test, clf.predict(X_test))}")
 
with open("cell_growth_model.pkl", "wb") as f:
    pickle.dump(clf, f)
 
with open("cell_growth_model.pkl", "rb") as f:
    clf = pickle.load(f)
 
def inference(some_list):
    with open("cell_growth_model.pkl", "rb") as f:
        model = pickle.load(f)
    label = model.predict(some_list)
    return state_names[label[0]]