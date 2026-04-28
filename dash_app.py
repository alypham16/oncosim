import os
import requests
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go

API = os.environ.get("API_URL", "http://localhost:5000")

app = Dash()
server = app.server

app.layout = html.Div([
    html.H2("Cell Growth Simulator"),

    html.Label("Initial sensitive cells"),
    dcc.Input(id="s1", type="number", value=45000),

    html.Label("Initial resistant cells"),
    dcc.Input(id="s2", type="number", value=5000),

    html.Label("Drug concentration (uM)"),
    dcc.Slider(id="drug", min=0, max=5, step=0.5, value=1.0,
               marks={i: str(i) for i in range(6)}),

    html.Label("Days"),
    dcc.Slider(id="days", min=7, max=60, step=1, value=30,
               marks={d: str(d) for d in [7, 20, 30, 45, 60]}),

    html.Button("Run Simulation", id="btn", n_clicks=0),

    html.Div(id="prediction"),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    Output("prediction", "children"),
    Input("btn", "n_clicks"),
    State("s1", "value"),
    State("s2", "value"),
    State("drug", "value"),
    State("days", "value"),
    prevent_initial_call=True,
)
def run(_, s1, s2, drug, days):
    total = (s1 or 0) + (s2 or 0)
    frac  = (s1 or 0) / total if total > 0 else 0.9

    resp   = requests.post(f"{API}/simulate",
                           json={"initial_state1": s1, "initial_state2": s2,
                                 "drug_concentration": drug, "days": days})
    data   = resp.json()
    result = data["result"]
    names  = data["state_names"]

    pred = requests.post(f"{API}/predict",
                         json={"drug_concentration": drug,
                               "initial_fraction": frac,
                               "days": days}).json()

    fig = go.Figure()
    for name in names:
        fig.add_trace(go.Scatter(x=result["days"], y=result[name], name=name))
    fig.update_layout(xaxis_title="Day", yaxis_title="Cell count")

    return fig, f"ML prediction: {pred['dominant_state']} will dominate"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)