import pandas as pd
import json
import plotly.express as px

import pathlib

from dash.dependencies import Input, Output
from flask import Flask, render_template_string, render_template
from flask.helpers import get_root_path
from dash import Dash
from dash import Dash, dcc, html


server = Flask(__name__,)


app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
)


dashapp = Dash()

# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
with server.app_context(), server.test_request_context():
    layout_dash = pathlib.Path(get_root_path(__name__)).joinpath("templates").joinpath("index.html")
    print('\n\n\n\nLayout_dash:\n',layout_dash,'\n\n\n')
    # html_body = render_template('index.html')
    with open(layout_dash, "r") as f:
        
        html_body = render_template_string(f.read())
        print('\n\n\n', html_body, '\n\n\n')
       

    app.index_string = (html_body)


# def visual():
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas",],
    "Amount": [4, 1, 2,],
})

fig = px.bar(df, x="Fruit", y="Amount", color="Fruit", width=650)
# fig.update_layout(
#         legend=dict(
#     orientation="h",
#     yanchor="bottom",
#     y=1.02,
#     xanchor="right",
#     x=1,
#     ))

sub_values = {
    'Day':[1, 2, 3, 4, 5],
    'Apples':[6, 7, 2, 4, 5],
    'Oranges':[8, 7, 6, 5, 4],
    'Bananas':[3, 9, 5, 11, 12],
    }

df_sub = pd.DataFrame(sub_values)

app.layout = html.Div([
    html.H1('Hello Dash'),
    html.Table([
        html.Tr(
            [
                html.Td(
                    [
                        dcc.Graph(
                        id='example-graph',
                        figure=fig,
                        )
                    ]
                ), 

                html.Td(
                    [
                        dcc.Graph(
                        id='subplot-graph',
                        animate=True,
                        ),
                    ]
                ), 
            ]
            ),
        ]),

    html.Pre(id='click-data'),
])

@app.callback(
    Output('click-data', 'children'),
    Output('subplot-graph', 'figure'),
    Input('example-graph', 'clickData'))
def display_click_data(clickdata):

    if not clickdata:
        clickdata = {'points':[{'x':'Apples'}]}

    print(f'\n\n{clickdata = }\n\n{type(clickdata) = }\n\n')
    input_data = clickdata['points'][0]
    column = input_data['x']
    
    filtered_df_sub = df_sub[['Day', column]]
   
    sub_fig = px.scatter(
        filtered_df_sub, 
        x="Day", 
        y=column,
        size=column,
        color=column, 
        
        # range_y=[0, df_sub.max()+1],
        # animation_group=column,
        
        ).update_traces(mode='lines+markers')
    

    return json.dumps(clickdata, indent=2), sub_fig


@server.route("/dash/")
def my_dash_app():
    return app.index()#render_template('templates/index.html',dash_app=app)