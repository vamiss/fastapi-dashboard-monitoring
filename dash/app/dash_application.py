from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
import psutil
import plotly
import monitor

UPDATE_INTERVAL = 200

dash_app = Dash(__name__, requests_pathname_prefix="/dashboard/", title="Monitoring", external_stylesheets=[dbc.themes.LUX])

header = dbc.Row(
    dbc.Col(
        [
            html.Div(style={"height": 30}),
            html.H1("Monitoring", className="text-center"),
        ]
    ),
    className="mb-4",
)
dash_app.layout = dbc.Container(
    [
        header,
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dcc.Graph(id="graph_cpu"),
                    ],
                    title="CPU"
                ),
                dbc.AccordionItem(
                    [
                        dcc.Graph(id="graph_ram"),
                    ],
                    title="RAM"
                ),
                dbc.AccordionItem(
                    [
                        dcc.Graph(id="graph_rom"),
                    ],
                    title="ROM"
                ),
                dbc.AccordionItem(
                    [
                        dcc.Graph(id="graph_network"),
                    ],
                    title="Network"
                ),
            ]
        ),
        dcc.Interval(id="timer", interval=UPDATE_INTERVAL),
    ],
    fluid=True,
    className='bg-dark',
)
    
@callback(Output("graph_cpu", 'figure'), Output("graph_ram", "figure"), Input("timer", 'n_intervals'))
def update_graph(n):
    monitor.update_df()
    
    processor_info = f"frequency - <span style='color:red'>{psutil.cpu_freq().current / 1000:.2f}</span> GHz, Cores - <span style='color:red'>{psutil.cpu_count(logical=False)}"

    cpu_graph_title = f"<i>Here is information about CPUs (like average load, load by each CPU, initial information about frequency, etc.):</i><br><br><span style='color:blue'>CPU Usage: {processor_info}</span>"


    traces_cpu = list()
    for t in monitor.df.columns[:-1]:
        traces_cpu.append(
            plotly.graph_objs.Line(
                x=monitor.df.index,
                y=monitor.df[t],
                name=t)
        )

    average_load = np.mean(monitor.df.iloc[:, :-1].values, axis=1)

    traces_cpu.append(
        plotly.graph_objs.Line(
            x=monitor.df.index,
            y=average_load,
            name='avg_load',
            line=dict(color='black', dash='dash'))
    )

    ram_graph_title = f"<i>Here is information about RAM (like ram, swap, memory capacity):</i>"

    traces_ram = [
        plotly.graph_objs.Line(
        x=monitor.df.index,
        y=monitor.df.iloc[:, -1],
        name='ram'),

        plotly.graph_objs.Line(
            x=monitor.df.index,
            y=[psutil.swap_memory().percent] * len(monitor.df.index),
            name='swap'),

        plotly.graph_objs.Line(
            x=monitor.df.index,
            y=[psutil.virtual_memory().total / (1024 ** 3)] * len(monitor.df.index),
            name='memory_capacity[GB]')
    ]

    return {"data": traces_cpu, "layout": {"template": "ggplot2", "title": cpu_graph_title}}, {"data": traces_ram, "layout": {"template": "ggplot2", "title": ram_graph_title}}

if __name__ == "__main__":
    monitor.update_df()
    dash_app.run_server(debug=True)