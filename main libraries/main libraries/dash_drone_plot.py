# ============================================================================
# File Name:        dash_drone_plot.py
# Author:           Vivek23
# Description:      Interactive Plotter on localhost website
# Dependencies:     Python >= 3.8
#                       - numpy     (pip install numpy)
#                       - pandas    (pip install pandas)
#                       - dash      (pip install dash)
#                       - plotly    (pip install plotly)
#                       - dash_bootstrap_components (pip install dash-bootstrap-components)
#                       - mavlab    (mavlab.py -> place it in the same folder)
#                       - senlab    (senlab.py -> place it in the same folder)
#
# Usage:            
#
# Requirements:     Don't change the base '.bin' filename so that you get a 
#                   '.mat' filename as '2023-11-28 10-47-30.bin-363701.mat'
# ============================================================================


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import mavlab
import senlab


# ----------------------------------- MAVLINK DATA PLOTTER -----------------------------------

def mavlink_plotter(path, filename, mission_name):
    path = '//'.join(path.split('\\')[:])
    filename = path + '//' + filename

    # params = ['AHR2','ATT','BARO_0','BARO_1','BAT_0','BAT_1','CTRL','CTUN','GPS_0','IMU_0','IMU_1','IMU_2','MODE','MOTB','POS','POWR','PSCD','PSCE','PSCN','RATE','RCIN','RCOU','TERR','XKF1_0','XKF1_1','XKF1_2','XKF2_0','XKF2_1','XKF2_2','XKF3_0','XKF3_1','XKF3_2','XKF4_0','XKF4_1','XKF4_2','XKF5_0','XKQ_0','XKQ_1','XKQ_2','XKT_0','XKT_1','XKT_2','XKV1_0','XKV2_0','XKY0_0','XKY0_1','XKY1_0','XKY1_1']

    # params = ['AHR2','ATT','BARO_0','BAT_0','CTUN','GPS_0','IMU_0','MODE','POS','POWR','RATE','RCIN','RCOU','TERR','XKF1_0','XKQ_0']

    params = ['AHR2','ATT','BARO_0','CTUN','GPS_0','IMU_0','MODE','POS','POWR','RATE','RCIN','RCOU','TERR','XKF1_0','XKQ_0']


    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

    a1 = html.Div(
        [
            html.Label('Parent Parameter'),
            dcc.Dropdown(
                id='x-main-dropdown',
                options=[{'label': param, 'value': param} for param in params],
                style={'color': 'black','text-align': 'center'},
                value=params[0]
            ),
            
        ],
    )

    a2 = html.Div(
        [
            html.Label('Sub Parameter'),
            dcc.Dropdown(
                id='x-sub-dropdown',
                style={'color': 'black'},
            ),
        ],
    )

    t1 = html.Div(id='table-info')

    t2 = html.Div(id='table-container')

    app.layout = html.Div([
        html.H2("M A V L I N K - D A T A - P L O T T E R", style={'text-align': 'center'}),
        html.Br(),
        dbc.Container([
            dbc.Row([dbc.Col(t1), dbc.Col(a1, width='2'), dbc.Col(a2, width='2'), dbc.Col(t2)], justify='center'),
        ],
            fluid=True,
            style={'text-align': 'center'},
        ),

        dcc.Graph(id='plot', style={'height': '70vh'})

    ])

    @app.callback(
        [Output('x-sub-dropdown', 'options'),
         Output('x-sub-dropdown', 'value')],
        [Input('x-main-dropdown', 'value')]
    )
    def update_x_sub_dropdown(x_main_value):
        labels = mavlab.label_wd(filename, params)
        sub_params = labels.get(x_main_value, [])
        default_value = sub_params[2] if sub_params else None
        return [{'label': label, 'value': label} for label in sub_params[2:]], default_value

    @app.callback(
        Output('plot', 'figure'),
        [Input('x-main-dropdown', 'value'),
         Input('x-sub-dropdown', 'value'),
         ]
    )
    def update_plot(x_main_value, x_sub_value):
        params = [x_main_value]
        data = mavlab.data(filename, params)
        time = mavlab.timedata_gpscor(filename, params)
        nums = np.arange(0, len(time[x_main_value])) / 10

        trace = go.Scatter(
            x=nums,
            y=data[x_main_value][x_sub_value],
            mode='lines',
            name=x_sub_value,
            line=dict(color='black')
        )

        layout = go.Layout(
            title=f"{x_sub_value} vs {'Time'}",
            xaxis=dict(title="Time (seconds)", tickfont=dict(color='black'), gridcolor='green'),
            yaxis=dict(title=x_sub_value, tickfont=dict(color='black'), gridcolor='green'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_gridcolor='green',
            yaxis_gridcolor='green',
            xaxis_gridwidth=1,
            yaxis_gridwidth=1,
            xaxis_tickformat='dashed',
            yaxis_tickformat='dashed',
        )

        return {'data': [trace], 'layout': layout}

    @app.callback(
        Output('table-container', 'children'),
        [Input('x-main-dropdown', 'value'),
         Input('x-sub-dropdown', 'value')]
    )
    def update_table(x_main_value, x_sub_value):
        if x_main_value is None or x_sub_value is None:
            return []

        data = mavlab.data(filename, [x_main_value])
        selected_data = data[x_main_value][x_sub_value]

        max_val = round(np.max(selected_data), 4)
        min_val = round(np.min(selected_data), 4)
        avg_val = round(np.mean(selected_data), 4)
        std_val = round(np.std(selected_data), 4)
        rms_val = round(np.sqrt(np.mean(selected_data ** 2)), 4)

        table_content = html.Table([
            html.Tr([
                html.Th('Statistic', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Maximum', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Minimum', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Mean', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Standard Deviation', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Root Mean Square', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ]),
            html.Tr([
                html.Th('Value', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(max_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(min_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(avg_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(std_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(rms_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ])
        ], style={'margin-top': '70px', 'margin-left': 'auto', 'margin-right': 'auto'})

        return table_content

    @app.callback(
        Output('table-info', 'children'),
        [Input('x-main-dropdown', 'value'),
         Input('x-sub-dropdown', 'value')]
    )
    def update_table(x_main_value, x_sub_value):
        if x_main_value is None or x_sub_value is None:
            return []

        time = mavlab.timedata_gpscor(filename, params)
        start_time = str(time['AHR2'][0].strftime('%H:%M:%S'))
        start_date = str(time['AHR2'][0].strftime('%Y-%m-%d'))

        table_content_2 = html.Table([
            html.Tr([
                html.Th('Mission Name', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Th('Date', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Th('Time', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ]),
            html.Tr([
                html.Td(mission_name, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(start_date, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(start_time, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ])
        ], style={'margin-top': '70px', 'margin-left': 'auto', 'margin-right': 'auto'})

        return table_content_2

    return app











# ----------------------------------- SENSOR DATA PLOTTER -----------------------------------

def tsm_plotter_d1(sensor_path,log_path,sensor_filename,log_filename,mission_name,latency_seconds,latency_milliseconds):
    sensor_path = '//'.join(sensor_path.split('\\')[:])
    log_path = '//'.join(log_path.split('\\')[:])
    sensor_filename = sensor_path + '//' + sensor_filename
    log_filename = log_path + '//' + log_filename

    sensor_labels = list(pd.read_csv(sensor_filename).columns[1:])

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

    a1 = html.Div(
        [
            html.Label('Sensor Parameter'),
            dcc.Dropdown(
                id='sensor-dropdown',
                options=[{'label': label, 'value': label} for label in sensor_labels],
                style={'color': 'black','text-align': 'center'},
                value=sensor_labels[0]
            ),
            
        ],
    )

    t1 = html.Div(id='table-info')

    t2 = html.Div(id='table-container')

    app.layout = html.Div([
        html.H2("S E N S O R - D A T A - P L O T T E R", style={'text-align': 'center'}),
        html.Br(),
        dbc.Container([
            dbc.Row([dbc.Col(t1), dbc.Col(a1, width='3'), dbc.Col(t2)], justify='center'),
        ],
            fluid=True,
            style={'text-align': 'center'},
        ),

        dcc.Graph(id='sensor-plot', style={'height': '70vh'})

    ])

    @app.callback(
        Output('sensor-plot', 'figure'),
        [Input('sensor-dropdown', 'value')]
    )
    def update_plot(selected_sensor):
        sensor_data = senlab.tsm_data_cor(log_filename, sensor_filename, latency_seconds, latency_milliseconds)
        nums = np.arange(0, len(sensor_data[selected_sensor])) / 10
        trace = go.Scatter(
            x=nums,
            y=sensor_data[selected_sensor],
            mode='lines',
            name=selected_sensor,
            line=dict(color='black')
        )

        layout = go.Layout(
            title=f"{selected_sensor} vs Time",
            xaxis=dict(title="Time (seconds)", tickfont=dict(color='black'), gridcolor='green'),
            yaxis=dict(title=selected_sensor, tickfont=dict(color='black'), gridcolor='green'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_gridcolor='green',
            yaxis_gridcolor='green',
            xaxis_gridwidth=1,
            yaxis_gridwidth=1,
            xaxis_tickformat='dashed',
            yaxis_tickformat='dashed',
        )

        return {'data': [trace], 'layout': layout}


    @app.callback(
        Output('table-container', 'children'),
        [Input('sensor-dropdown', 'value')]
    )
    def update_table(sensor_parameter):
        if sensor_parameter is None:
            return []

        sensor_data = senlab.tsm_data_cor(log_filename, sensor_filename, latency_seconds, latency_milliseconds)
        selected_data = sensor_data[sensor_parameter]

        max_val = round(np.max(selected_data), 4)
        min_val = round(np.min(selected_data), 4)
        avg_val = round(np.mean(selected_data), 4)
        std_val = round(np.std(selected_data), 4)
        rms_val = round(np.sqrt(np.mean(selected_data ** 2)), 4)

        table_content = html.Table([
            html.Tr([
                html.Th('Statistic', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Maximum', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Minimum', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Mean', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Standard Deviation', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td('Root Mean Square', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ]),
            html.Tr([
                html.Th('Value', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(max_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(min_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(avg_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(std_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(rms_val, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ])
        ], style={'margin-top': '70px', 'margin-left': 'auto', 'margin-right': 'auto'})

        return table_content

    @app.callback(
        Output('table-info', 'children'),
        [Input('sensor-dropdown', 'value')]
    )
    def update_table(sensor_parameter):
        if sensor_parameter is None:
            return []
        params = ['AHR2']
        time = mavlab.timedata_gpscor(log_filename, params)
        start_time = str(time['AHR2'][0].strftime('%H:%M:%S'))
        start_date = str(time['AHR2'][0].strftime('%Y-%m-%d'))

        table_content_2 = html.Table([
            html.Tr([
                html.Th('Mission Name', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Th('Date', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Th('Time', style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ]),
            html.Tr([
                html.Td(mission_name, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(start_date, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'}),
                html.Td(start_time, style={'border': '1px solid black', 'text-align': 'center', 'padding': '5px'})
            ])
        ], style={'margin-top': '70px', 'margin-left': 'auto', 'margin-right': 'auto'})

        return table_content_2

    return app