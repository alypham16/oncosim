from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objects as go

from backend import fit_and_store, get_fit, predict, simulate

app = Dash()
server = app.server


app.layout = html.Div([
    html.H2("Cell Growth Simulator"),

    html.Label("Time"),
    dcc.Input(id="time", value="0,1,2,3,4,5"),

    html.Label("Counts"),
    dcc.Input(id="counts", value="1000,2000,4000,7000,9000,10000"),

    html.Label("Drug"),
    dcc.Slider(id="drug", min=0, max=5, step=0.1, value=1),

    html.Button("Run", id="btn"),

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
    prevent_initial_call=True
)

def run(_, time_str, count_str, drug):

    time = list(map(float, time_str.split(",")))
    counts = list(map(float, count_str.split(",")))

    # 1. FIT + STORE IN REDIS
    params = fit_and_store(time, counts)

    # 2. READ BACK FROM REDIS
    stored = get_fit()

    # 3. ML PREDICTION
    label = predict(stored, drug)

    # 4. SIMULATION
    sim = simulate(stored, drug=drug)

    # 5. PLOT
    fig = go.Figure()

    # raw data
    fig.add_trace(go.Scatter(
        x=time,
        y=counts,
        mode="markers+lines",
        name="User Data"
    ))

    # fitted curve
    fig.add_trace(go.Scatter(
        x=sim["days"],
        y=sim["counts"],
        mode="lines",
        name="Logistic Fit (Model)"
    ))
    return fig, "Resistant" if label else "Sensitive"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)