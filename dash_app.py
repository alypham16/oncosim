from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go

from backend import fit_and_store, get_fit, predict_resistance, run_simulation

app = Dash()
server = app.server

app.layout = html.Div([
    html.H2("TNBC Cell Population Growth and Drug Resistance Simulator"),
    html.H4("Enter time points (hours) and cell counts to fit the growth model."),
    html.H4("Then select a chemotherapeutic drug, TNBC cell line, and exposure type to predict resistance and simulate growth under treatment."),

    html.Label("Time (hours)"),
    dcc.Input(id = "time", value = "0,4,8,12,16"),

    html.Label("Cell Counts"),
    dcc.Input(id = "counts", value = "1000,2000,4000,7000,9000"),

    html.Label("Cell Line"),
    dcc.Dropdown(
        id = "cell_line",
        options = [
            {"label": "MDA-MB-231", "value": "231"},
            {"label": "MDA-MB-468", "value": "468"},
            {"label": "HCC1806", "value": "1806"},
            {"label": "BT-49", "value": "549"}
        ],
        value="231"
    ),

    html.Label("Drug"),
    dcc.Dropdown(
        id = "drug",
        options = [
            {"label": "Cisplatin", "value": "cisplatin"},
            {"label": "Docetaxel", "value": "docetaxel"},
            {"label": "Olaparib", "value": "olaparib"},
            {"label": "Paclitaxel", "value": "paclitaxel"},
            {"label": "Gemcitabine", "value": "gemcitabine"},
            {"label": "Talazoparib", "value": "talazoparib"},
            {"label": "Epirubicin", "value": "epirubicin"},
            {"label": "Cyclophosphamide", "value": "cyclophosphamide"}
        ],
        value="cisplatin"
    ),

    html.Button("Run", id = "btn", n_clicks = 0),

    html.Div(id="prediction"),
    dcc.Graph(id="graph")
])


@app.callback(
    Output("graph", "figure"),
    Output("prediction", "children"),
    Input("btn", "n_clicks"),
    State("time", "value"),
    State("counts", "value"),
    State("drug", "value"),
    State("cell_line", "value"),
    prevent_initial_call=True
)

def run(_, time_str, count_str, drug, cell_line):

    time = list(map(float, time_str.split(",")))
    counts = list(map(float, count_str.split(",")))

    if len(time) != len(counts):
        return {}, "Error: time and counts must match"

    params = fit_and_store(time, counts)
    stored = get_fit()

    resistance = float(predict_resistance(stored, drug, cell_line))

    sim = run_simulation(stored, drug, resistance)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x = time, y = counts, mode = "markers", name = "Data"))

    fig.add_trace(go.Scatter(x = sim["hours"], y = sim["sensitive"], name = "Sensitive"))

    fig.add_trace(go.Scatter(x = sim["hours"], y = sim["resistant"], name = "Resistant"))

    fig.add_trace(go.Scatter(x = sim["hours"], y = sim["total"], name = "Total"))

    fig.update_layout(
        xaxis_title = "Time (hours)",
        yaxis_title = "Cell Count")

    label = f"Resistance probability: {resistance:.2f}"

    return fig, f"Prediction: {label}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)