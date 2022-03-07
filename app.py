import redis
import json
import numpy as np
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dash.dependencies import Input, Output

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
r = redis.Redis(host='152.3.65.126', port=6379)
app.oneMin, app.oneHour, app.vm = [],[],[]
app.cpu_data = json.loads(r.get('zz188-proj3-output'))
app.layout = html.Div(
    html.Div([
        html.H4(children='CPU Resources Monitor', 
        style={'textAlign': 'center','fontSize':'30px'}),
        html.Div(id='realtime'),
        dcc.Graph(id='realtime-cpu'),
        # dcc.Graph(id='live-update-graph2'),
        dcc.Interval(
            id='interval-component',
            interval=3*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('realtime', 'children'),
              Input('interval-component', 'n_intervals'))
def update_time(n):
    app.cpu_data = json.loads(r.get('zz188-proj3-output'))
    return [html.Span(app.cpu_data['time'])]

@app.callback(Output('realtime-cpu', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_cpu(n):
    data_points = 20
    app.oneMin.append([app.cpu_data['cpu_%d_1min_ewma'%i] for i in range(4)])
    app.oneHour.append([app.cpu_data['cpu_%d_1h_ewma'%i] for i in range(4)])
    app.vm.append(app.cpu_data['VM_used_past_5min_avg'])
    if len(app.oneMin) > data_points:
        app.oneMin = app.oneMin[1:]
        app.oneHour = app.oneHour[1:]
        app.vm = app.vm[1:]
    
    # set colors for each cpu
    colors = ['rgb(163,214,245)','rgb(225,179,120)','rgb(159,2,81)','rgb(111,84,149)','rgb(213,177,0)']
    # plot fig
    figs = make_subplots(
        rows = 3,
        cols = 1,
        subplot_titles = (
            "EWMA(60s) of CPU Utilization",
            "EWMA(60min) of CPU Utilization",
            "EWMA(5min) of VM Utilization"
        ),
        shared_xaxes=True
        # vertical_spacing = 0.03
    )
    for i in range(4): # i is the index of cpu
        # print(app.oneMin)
        figs.add_trace(go.Scatter(x=np.arange(len(app.oneMin)*4), y=np.array(app.oneMin)[:,i], name="cpu_%d_oneMin"%i, mode="lines", line={'color':colors[i]}), row=1, col=1)
        figs.add_trace(go.Scatter(x=np.arange(len(app.oneHour)*4), y=np.array(app.oneHour)[:,i], name="cpu_%d_oneHour"%i, mode="lines", line={'color':colors[i]}), row=2, col=1)
    figs.add_trace(go.Scatter(x=np.arange(len(app.vm)*4), y=np.array(app.vm), name="vm_5min", mode="lines", fill = 'tozeroy', line={'color':colors[4]}), row=3, col=1)
    figs.update_xaxes(title_text = 'Time (s)')
    figs.update_yaxes(title_text = 'Utilization (%)')
    figs.update_layout(
        width = 1500,
        height = 800
    )
    return figs



if __name__ == '__main__':
    app.run_server(debug=True,port=5117,host='0.0.0.0')