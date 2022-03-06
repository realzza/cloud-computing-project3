import redis
import json
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
def prepare_dashboard():
    newd = {}
    r = redis.Redis(host='localhost', port=6379, db=0)
    raw_d = json.loads(r.get('zz188-proj3-output'))
    
    newd['cpu_metric'] = ["_".join(k.split("_")[:2]) for k in list(raw_d.keys())]
    newd['cpu_metric_value'] = list(raw_d.values())
    newd['time_range'] = ['1min',"1h",'1min',"1h",'1min',"1h",'1min',"1h","5min"]
    df = pd.DataFrame(newd)
    return df

df = prepare_dashboard()
fig = px.bar(df, x="cpu_metric", y="cpu_metric_value", color="time_range", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Server Resource Monitor Dashboard'),

    html.Div(children='''
        Designed by Ziang Zhou
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    # app.run_server(debug=True, host="0.0.0.0", port="8811")
    app.run_server(debug=True, port="8812")