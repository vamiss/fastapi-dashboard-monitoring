from dash import Dash, html, dcc, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
import numpy as np
import psutil
import plotly
import monitor
from dash_table import DataTable

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

cpu_checklist = dbc.Row(
    dbc.Col(
        [
            html.H5("Select CPU data to display:"),
            dcc.Checklist(
                id='cpu_checklist',
                options=[
                    {'label': f'CPU {i+1}', 'value': f'cpu{i+1}'} for i in range(monitor.CPU_COUNT)
                ] + [{'label': 'Average Load', 'value': 'avg_load'}],
                value=[f'cpu{i+1}' for i in range(monitor.CPU_COUNT)] + ['avg_load'],
                inline=True,
                className='bg-light text-dark'
            )
        ]
    )
)

dash_app.layout = dbc.Container(
    [
        header,
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        cpu_checklist,
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
                        DataTable(id="table_network_connections"),
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


@dash_app.callback(
    [
        Output("graph_cpu", 'figure'),
        Output("graph_ram", "figure"),
        Output("graph_rom", "figure"),
        Output("graph_network", "figure"),
        Output("table_network_connections", "data"),
        Output("table_network_connections", "columns")
    ],
    [
        Input("timer", 'n_intervals'),
        Input("cpu_checklist", 'value')
    ]
)
def update_graph(n, cpu_selected):
    monitor.update_df()
    
    processor_info = f"frequency - <span style='color:red'>{psutil.cpu_freq().current / 1000:.2f}</span> GHz, Cores - <span style='color:red'>{psutil.cpu_count(logical=False)}"

    cpu_graph_title = f"<i>Here is information about CPUs (like average load, load by each CPU, initial information about frequency, etc.):</i><br><br><span style='color:blue'>CPU Usage: {processor_info}</span>"

    traces_cpu = []
    for t in cpu_selected:
        if t == 'avg_load':
            average_load = np.mean(monitor.df.iloc[:, :-1].values, axis=1)
            traces_cpu.append(
                plotly.graph_objs.Scatter(
                    x=monitor.df.index,
                    y=average_load,
                    name='avg_load',
                    line=dict(color='black', dash='dash')
                )
            )
        else:
            traces_cpu.append(
                plotly.graph_objs.Scatter(
                    x=monitor.df.index,
                    y=monitor.df[t],
                    name=t
                )
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

    rom_graph_title = f"<i>Here is information about ROM (like disk usage, total disk space):</i>"

    disk_io_info = psutil.disk_io_counters()
    disk_usage_info = psutil.disk_usage('/')

    traces_rom = [
        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[disk_usage_info.used / (1024 ** 3)],  # Disk used in GB
            name='disk_used[GB]',
            mode='markers',
            marker=dict(color='blue', size=10)
            ),
        
        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[disk_io_info.read_bytes / (1024 ** 3)],  # Disk read in GB
            name='disk_read[GB]',
            mode='markers',
            marker=dict(color='blue', size=10)
            ),
        
        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[disk_io_info.write_bytes / (1024 ** 3)],  # Disk write in GB
            name='disk_write[GB]',
            mode='markers',
            marker=dict(color='red', size=10)
            ),
        
        plotly.graph_objs.Line(
            x=monitor.df.index,
            y=[disk_usage_info.percent] * len(monitor.df.index),
            name='disk_usage_percent'
        ),

        plotly.graph_objs.Line(
            x=monitor.df.index,
            y=[disk_usage_info.total / (1024 ** 3)] * len(monitor.df.index),
            name='total_disk_space[GB]'
        )
    ]

    net_graph_title = f"<i>Here is information about Network (like send/receive speed, total data sent/received, connections):</i>"
    
    network_io_info = psutil.net_io_counters()
    connections = psutil.net_connections()

    traces_network = [
        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[network_io_info.bytes_sent / (1024 ** 2)],  # Sent in MB
            name='bytes_sent[MB]',
            mode='markers',
            marker=dict(color='blue', size=10)
            ),

        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[network_io_info.bytes_recv / (1024 ** 2)],  # Received in MB
            name='bytes_recv[MB]',
            mode='markers',
            marker=dict(color='red', size=10)
            ),

        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[network_io_info.packets_sent],
            name='packets_sent',
            mode='markers',
            marker=dict(color='green', size=10)
            ),

        plotly.graph_objs.Line(
            x=[monitor.df.index[-1]],
            y=[network_io_info.packets_recv],
            name='packets_recv',
            mode='markers',
            marker=dict(color='orange', size=10)
            )
    ]

    connection_data = [
        {
            "fd": conn.fd,
            "family": str(conn.family),
            "type": str(conn.type),
            "local_address": f"{conn.laddr.ip}:{conn.laddr.port}",
            "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "",
            "status": conn.status
        }
        for conn in connections if conn.status == 'ESTABLISHED' and conn.laddr.ip != '127.0.0.1'
    ]
    connection_columns = [
        {"name": "File Descriptor", "id": "fd"},
        {"name": "Family", "id": "family"},
        {"name": "Type", "id": "type"},
        {"name": "Local Address", "id": "local_address"},
        {"name": "Remote Address", "id": "remote_address"},
        {"name": "Status", "id": "status"}
    ]

    return {
        "data": traces_cpu,
        "layout": {"template": "ggplot2", "title": cpu_graph_title}
    }, {
        "data": traces_ram,
        "layout": {"template": "ggplot2", "title": ram_graph_title}
    }, {
        "data": traces_rom,
        "layout": {"template": "ggplot2", "title": rom_graph_title}
    }, {
        "data": traces_network,
        "layout": {"template": "ggplot2", "title": net_graph_title}
    }, connection_data, connection_columns

if __name__ == "__main__":
    monitor.update_df()
    dash_app.run_server(debug=True)

""" 
What about tempature? I can't display it using psutil on Windows.
I've found OpenHardwareMonitor for displaying temperature on Windows,
but it ended up I decided not to display it at all. Maybe, I'll add it later.
"""