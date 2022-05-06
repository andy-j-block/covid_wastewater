import plotly.express as px
from dash import Dash, Input, Output, dcc, html
import pandas as pd
from datetime import datetime, timezone
import time
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

app = Dash(__name__)
app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}


class DataHandler:

    def __init__(self, interp_data: str, raw_data: str, positivity: str):
        self.interp_data = pd.read_csv(interp_data)
        self.raw_data = pd.read_csv(raw_data)
        self.positivity = pd.read_csv(positivity)
        self.wastewater_plants = self.interp_data['wrrf_name'].unique()
        self.wastewater_time_series = pd.to_datetime(self.interp_data['sample_date'])
        self.determine_timespan()


    def produce_fig(self, df, fig_kwargs):
        fig = px.bar(df, **fig_kwargs)
        return fig


    def determine_timespan(self):
        wastewater_time_series = pd.to_datetime(self.interp_data['sample_date'])
        positivity_time_series = pd.to_datetime(self.positivity['DATE'])

        self.min_date = wastewater_time_series.min() if wastewater_time_series.min() > positivity_time_series.min() \
                        else positivity_time_series.min()

        self.max_date = wastewater_time_series.max() if wastewater_time_series.max() < positivity_time_series.max() \
                        else positivity_time_series.max()

        for date in [self.min_date, self.max_date]:
            date.strftime('%m/%d/%Y').replace(tzinfo=timezone.utc)


    def update_fig(self, dropdown_selections, interp_selection, end_date, start_date):
        # interpolation selection
        starting_df = self.interp_data.copy() if interp_selection == 'On' else self.raw_data.copy()
        starting_df['sample_date'] = pd.to_datetime(starting_df['sample_date'])

        # end_date = datetime.strptime(end_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)
        # start_date = datetime.strptime(start_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)


        # timespan filter
        starting_df = starting_df[(starting_df['sample_date'] >= start_date) &
                                  (starting_df['sample_date'] <= end_date)]

        # plant dropdown
        df = pd.DataFrame(columns=starting_df.columns)
        for dropdown in dropdown_selections:
            df = df.append(starting_df[starting_df['wrrf_name'] == dropdown])

        fig = self.produce_fig(df, self.wastewater_fig_kwargs)
        return fig

    def update_positivity(self, end_date, start_date):
        df = self.positivity.copy()

        # timespan filter
        df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]

        fig = self.produce_fig(df, self.positivity_fig_kwargs)
        return fig


    def debugging(self, values):
        return f'Here are your values: {values} of type {type(values)}'


data_handler = DataHandler('wastewater_stats_interpolated.csv', 'wastewater_stats_prepared.csv',
                           'testing_data_prepared.csv')


app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div([
    html.Div(children=[
        html.H1(children='COVID Wastewater Surveillance')]),

    html.Div(children=[

        html.Div(children=[
            html.Label('Wastewater Plants'),
            dcc.Dropdown(options=data_handler.wastewater_plants,
                         value=data_handler.wastewater_plants,
                         id='wastewater_dropdown',
                         placeholder='Select one or more plants',
                         multi=True),
            html.Div(id='dropdown_output')

        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Interpolation Status'),
            dcc.RadioItems(id='interp_buttons', options=['On', 'Off'], value='On'),
            html.Br(),
            html.Label('Date Range'),
            html.Br(),
            dcc.DatePickerRange(id='date_range',
                                min_date_allowed=data_handler.min_date,
                                max_date_allowed=data_handler.max_date,
                                start_date=data_handler.min_date,
                                end_date=data_handler.max_date)

        ], style={'padding': 10, 'flex': 1}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    html.Div(children=[

        dcc.Graph(id='main_graph')

    ]),

    html.Div(children=[

        dcc.Graph(id='positivity_graph')

    ])
])


@app.callback(
    Output('main_graph', 'figure'),
    [Input('wastewater_dropdown', 'value'),
     Input('interp_buttons', 'value'),
     Input('date_range', 'end_date'),
     Input('date_range', 'start_date')]
)
def update_wastewater_fig(dropdown, interp, end_date, start_date):
    print(f'wastewater end date: {end_date}, start date: {start_date}')

    # try:
    #     end_date = datetime.strptime(end_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)
    # except:
    #     end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    #
    # try:
    #     start_date = datetime.strptime(start_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)
    # except:
    #     pass
    #     # start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)


    fig = data_handler.update_fig(dropdown, interp, end_date, start_date)
    return fig


@app.callback(
    Output('positivity_graph', 'figure'),
    [Input('date_range', 'end_date'),
     Input('date_range', 'start_date')]
)
def update_positivity_fig(end_date, start_date):
    print(f'positivity end date: {end_date}, start date: {start_date}')

    ##TODO this is broken
    try:
        end_date = datetime.strptime(end_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)
    except:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)

    try:
        start_date = datetime.strptime(start_date, '%m/%d/%Y').replace(tzinfo=timezone.utc)
    except:
        pass
        # start_date = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)

    fig = data_handler.update_positivity(end_date, start_date)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
